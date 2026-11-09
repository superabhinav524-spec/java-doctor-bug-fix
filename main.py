"""
Main WSGI entrypoint for JavaDoctor (Vercel & Local).
Zero third-party dependencies - standard Python only.
"""

import json
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from javadoctor.core.engine import JavaDoctorEngine
from javadoctor.rules import registry

PUBLIC_DIR = BASE_DIR / "public"
if not PUBLIC_DIR.exists():
    PUBLIC_DIR = BASE_DIR / "javadoctor" / "web" / "static"


def app(environ, start_response):
    """
    Standard WSGI Application (PEP 3333).
    Compatible with Vercel Serverless Functions, AWS Lambda, and local servers.
    """
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/").rstrip("/")
    if not path:
        path = "/"

    # Handle CORS preflight
    if method == "OPTIONS":
        headers = [
            ("Content-Type", "text/plain"),
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type"),
        ]
        start_response("200 OK", headers)
        return [b"OK"]

    def json_response(data, status="200 OK"):
        body = json.dumps(data, indent=2).encode("utf-8")
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type"),
        ]
        start_response(status, headers)
        return [body]

    def file_response(file_path, content_type):
        if not file_path.exists():
            return json_response({"error": "Static file not found"}, status="404 Not Found")
        body = file_path.read_bytes()
        headers = [
            ("Content-Type", content_type),
            ("Content-Length", str(len(body))),
            ("Access-Control-Allow-Origin", "*"),
            ("Cache-Control", "public, max-age=3600"),
        ]
        start_response("200 OK", headers)
        return [body]

    # Handle GET requests (Static Files & API)
    if method == "GET":
        if path in ["/", "/index.html"]:
            return file_response(PUBLIC_DIR / "index.html", "text/html; charset=utf-8")
        elif path == "/styles.css":
            return file_response(PUBLIC_DIR / "styles.css", "text/css; charset=utf-8")
        elif path == "/app.js":
            return file_response(PUBLIC_DIR / "app.js", "application/javascript; charset=utf-8")
        elif path.endswith("/rules"):
            rules_data = [
                {
                    "id": r.rule_id,
                    "name": r.name,
                    "severity": r.severity.value,
                    "category": r.category.value,
                    "description": r.description,
                    "why": r.why,
                }
                for r in registry.all_rules()
            ]
            return json_response({"rules": rules_data})
        else:
            return json_response({"error": f"Not found: {path}"}, status="404 Not Found")

    # Handle POST requests (Scan, Fix, Verify)
    if method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            content_length = 0

        body_bytes = environ["wsgi.input"].read(content_length) if content_length > 0 else b""
        try:
            data = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except json.JSONDecodeError:
            return json_response({"error": "Invalid JSON"}, status="400 Bad Request")

        engine = JavaDoctorEngine()

        if path.endswith("/scan"):
            code = data.get("code", "")
            report = engine.scan_code(code)
            return json_response(report.to_dict())

        elif path.endswith("/fix"):
            code = data.get("code", "")
            fixed_code, report = engine.fix_code(code, verify=True)
            return json_response({
                "original_code": code,
                "fixed_code": fixed_code,
                "diff": report.diff,
                "is_fixed": report.is_fixed,
                "bugs": [b.to_dict() for b in report.bugs],
                "verification_passed": report.verification_passed,
                "verification_message": report.verification_message,
            })

        elif path.endswith("/verify"):
            code = data.get("code", "")
            if not engine.verifier.is_available():
                return json_response({
                    "passed": False,
                    "message": "javac compiler is not available in the serverless cloud environment (local JDK required for full compiler verification).",
                })
            passed, out, errs = engine.verifier.verify_code(code)
            return json_response({
                "passed": passed,
                "output": out,
                "errors": errs,
            })

        return json_response({"error": f"Endpoint not found: {path}"}, status="404 Not Found")

    return json_response({"error": "Method not allowed"}, status="405 Method Not Allowed")


# Export both `app` and `handler` for full Vercel compatibility
handler = app

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = int(os.environ.get("PORT", 8080))
    print(f"\n=======================================================")
    print(f" JavaDoctor Web Dashboard running at: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    server = make_server("127.0.0.1", port, app)
    server.serve_forever()
