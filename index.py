"""
Vercel Serverless Function entrypoint for JavaDoctor.
"""

import http.server
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any
from urllib.parse import urlparse

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from javadoctor.core.engine import JavaDoctorEngine
from javadoctor.rules import registry

PUBLIC_DIR = PROJECT_ROOT / "public"


class handler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        if path.endswith("/rules"):
            rules_data = []
            for r in registry.all_rules():
                rules_data.append({
                    "id": r.rule_id,
                    "name": r.name,
                    "severity": r.severity.value,
                    "category": r.category.value,
                    "description": r.description,
                    "why": r.why
                })
            self._send_json({"rules": rules_data})
            return

        # Serve static files as fallback if accessed directly
        if path == "/" or path == "/index.html":
            self._serve_file(PUBLIC_DIR / "index.html", "text/html; charset=utf-8")
        elif path == "/styles.css":
            self._serve_file(PUBLIC_DIR / "styles.css", "text/css; charset=utf-8")
        elif path == "/app.js":
            self._serve_file(PUBLIC_DIR / "app.js", "application/javascript; charset=utf-8")
        else:
            self._send_json({"error": "Not found", "path": self.path}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else ""

        try:
            data = json.loads(post_body) if post_body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, status=400)
            return

        engine = JavaDoctorEngine()

        if path.endswith("/scan"):
            code = data.get("code", "")
            file_path = data.get("path")

            if file_path and os.path.exists(file_path):
                if os.path.isdir(file_path):
                    summary = engine.scan_directory(file_path)
                    self._send_json(summary.to_dict())
                    return
                else:
                    report = engine.scan_file(file_path)
                    self._send_json(report.to_dict())
                    return
            else:
                report = engine.scan_code(code)
                self._send_json(report.to_dict())
                return

        elif path.endswith("/fix"):
            code = data.get("code", "")
            fixed_code, report = engine.fix_code(code, verify=True)
            self._send_json({
                "original_code": code,
                "fixed_code": fixed_code,
                "diff": report.diff,
                "is_fixed": report.is_fixed,
                "bugs": [b.to_dict() for b in report.bugs],
                "verification_passed": report.verification_passed,
                "verification_message": report.verification_message
            })
            return

        elif path.endswith("/fix_file"):
            file_path = data.get("file_path", "")
            if not os.path.isfile(file_path):
                self._send_json({"error": f"File not found: {file_path}"}, status=404)
                return
            report = engine.fix_file(file_path, dry_run=False, backup=True, verify=True)
            self._send_json(report.to_dict())
            return

        elif path.endswith("/verify"):
            code = data.get("code", "")
            if not engine.verifier.is_available():
                self._send_json({
                    "passed": False,
                    "message": "javac compiler is not available in the serverless cloud environment (local JDK required for full compiler verification)."
                })
                return
            passed, out, errs = engine.verifier.verify_code(code)
            self._send_json({
                "passed": passed,
                "output": out,
                "errors": errs
            })
            return

        self._send_json({"error": "Endpoint not found", "path": self.path}, status=404)

    def _serve_file(self, file_path: Path, content_type: str):
        if not file_path.exists():
            self._send_json({"error": f"Static file not found"}, status=404)
            return
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, data: Dict[str, Any], status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)
