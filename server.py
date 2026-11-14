#!/usr/bin/env python3
"""PharmaGuard AI — Local REST API and Web Application Server.

Pure Python 3 standard library, zero external pip dependencies.
"""

import sys
import json
import mimetypes
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from pharmaguard.engine import ClinicalSafetyEngine
from pharmaguard.scheduler import ScheduleOptimizer
from pharmaguard.interactions import DRUG_REGISTRY


class PharmaGuardHandler(BaseHTTPRequestHandler):

    engine = ClinicalSafetyEngine()
    scheduler = ScheduleOptimizer()
    static_dir = Path(__file__).parent / "static"

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/drugs":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            drugs = [
                {
                    "key": k,
                    "name": v["name"],
                    "brand": v["brand"],
                    "class": v["class"],
                    "default_dose": v["default_dose"],
                    "default_time": v["default_time"],
                    "food_warnings": v["food_warnings"]
                }
                for k, v in DRUG_REGISTRY.items()
            ]
            self.wfile.write(json.dumps({"drugs": drugs}, indent=2).encode("utf-8"))
            return

        if path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "PharmaGuard AI"}).encode("utf-8"))
            return

        # Serve static frontend files
        if path == "/" or path == "":
            file_path = self.static_dir / "index.html"
        else:
            file_path = self.static_dir / path.lstrip("/")

        if file_path.is_file():
            mime_type, _ = mimetypes.guess_type(str(file_path))
            self.send_response(200)
            self.send_header("Content-Type", mime_type or "text/plain")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(file_path.read_bytes())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
            return

        if path == "/api/audit":
            medications = payload.get("medications", [])
            result = self.engine.audit_regimen(medications)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode("utf-8"))
            return

        if path == "/api/reschedule":
            regimen = payload.get("regimen", [])
            interactions = payload.get("interactions", [])
            schedule = self.scheduler.build_schedule(regimen, interactions)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(schedule, indent=2).encode("utf-8"))
            return

        if path == "/api/sbar":
            audit_result = payload.get("audit_result", {})
            patient_name = payload.get("patient_name", "Patient Jane Doe")
            age = payload.get("age", 74)
            sbar_text = self.engine.generate_sbar_note(audit_result, patient_name, age)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"sbar": sbar_text}, indent=2).encode("utf-8"))
            return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Endpoint not found")

    def log_message(self, format, *args):
        # Quiet logger for clean test output
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def run_server(port: int = 8080):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, PharmaGuardHandler)
    print(f"============================================================")
    print(f"  PharmaGuard AI Server listening at http://127.0.0.1:{port}")
    print(f"  Zero external dependencies. Press Ctrl+C to stop.")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        httpd.server_close()


if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1] in ("--port", "-p") and len(sys.argv) > 2:
        port = int(sys.argv[2])
    run_server(port)
