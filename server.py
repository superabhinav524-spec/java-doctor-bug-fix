"""
Root server entrypoint for local execution and Vercel.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from api.index import handler

if __name__ == "__main__":
    from javadoctor.web.server import start_server
    start_server()
