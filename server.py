#!/usr/bin/env python3
"""PharmaGuard AI — local REST API and web application server.

Pure Python 3 standard library. No external pip dependencies.
"""

from __future__ import annotations

import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from pharmaguard.engine import ClinicalSafetyEngine, parse_patient
from pharmaguard.interactions import DISCLAIMER, DRUG_REGISTRY, KNOWLEDGE_BASE_META
from pharmaguard.scheduler import ScheduleOptimizer


class PharmaGuardHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class PharmaGuardHandler(BaseHTTPRequestHandler):
    engine = ClinicalSafetyEngine()
    static_dir = (Path(__file__).parent / "static").resolve()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _set_common_headers(self, content_type: str, cache: str = "no-store") -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self._set_common_headers("application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, status: int = 200) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self._set_common_headers("text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict | None:
        """Return a JSON object, or None when the request body is invalid."""
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            length = 0
        if length <= 0:
            return {}
        if length > 2_000_000:
            return None
        body = self.rfile.read(length)
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        return payload if isinstance(payload, dict) else None

    def _safe_static_path(self, raw_path: str) -> Path | None:
        relative = raw_path.lstrip("/")
        if not relative:
            relative = "index.html"
        candidate = (self.static_dir / relative).resolve()
        try:
            if candidate == self.static_dir or candidate.is_relative_to(self.static_dir):
                return candidate
        except AttributeError:  # pragma: no cover - Python < 3.9 fallback
            if str(candidate).startswith(str(self.static_dir) + os.sep):
                return candidate
        return None

    # ------------------------------------------------------------------
    # HTTP verbs
    # ------------------------------------------------------------------
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._set_common_headers("text/plain")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self._send_json({
                "status": "healthy",
                "service": "PharmaGuard AI",
                "knowledge_base": KNOWLEDGE_BASE_META["version"],
            })
            return

        if path == "/api/meta":
            self._send_json({
                "knowledge_base": KNOWLEDGE_BASE_META,
                "disclaimer": DISCLAIMER,
                "features": {
                    "label_scan": True,
                    "constraint_scheduler": True,
                    "calendar_export": True,
                    "sbar_export": True,
                },
            })
            return

        if path == "/api/drugs":
            drugs = [
                {
                    "key": key,
                    "name": value["name"],
                    "brand": value["brand"],
                    "class": value["class"],
                    "default_dose": value["default_dose"],
                    "default_time": value["default_time"],
                    "food_warnings": value["food_warnings"],
                    "aliases": value.get("aliases", []),
                    "schedule": value.get("schedule", {}),
                }
                for key, value in DRUG_REGISTRY.items()
            ]
            self._send_json({"drugs": drugs, "count": len(drugs)})
            return

        file_path = self._safe_static_path(path)
        if file_path is None or not file_path.is_file():
            self._send_text("404 Not Found", 404)
            return

        mime_type, _ = mimetypes.guess_type(str(file_path))
        body = file_path.read_bytes()
        self.send_response(200)
        self._set_common_headers(
            mime_type or "application/octet-stream",
            cache="no-cache",
        )
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        payload = self._read_json()

        if payload is None:
            self._send_json({"error": "Invalid JSON body"}, 400)
            return

        try:
            if path == "/api/audit":
                medications = payload.get("medications", [])
                if not isinstance(medications, list):
                    self._send_json({"error": "medications must be a list of strings"}, 400)
                    return
                dose_overrides = payload.get("dose_overrides", {})
                if not isinstance(dose_overrides, dict):
                    self._send_json({"error": "dose_overrides must be an object"}, 400)
                    return
                patient, patient_error = parse_patient(payload.get("patient"))
                if patient_error:
                    self._send_json({"error": patient_error}, 400)
                    return
                result = self.engine.audit_regimen(medications, dose_overrides, patient)
                self._send_json(result)
                return

            if path == "/api/reschedule":
                regimen = payload.get("regimen", [])
                interactions = payload.get("interactions", [])
                if not isinstance(regimen, list) or not isinstance(interactions, list):
                    self._send_json({"error": "regimen and interactions must be lists"}, 400)
                    return
                # A fresh optimizer per request keeps solver state thread-safe.
                self._send_json(ScheduleOptimizer().build_schedule(regimen, interactions))
                return

            if path == "/api/sbar":
                audit_result = payload.get("audit_result", {})
                if not isinstance(audit_result, dict):
                    self._send_json({"error": "audit_result must be an object"}, 400)
                    return
                raw_name = payload.get("patient_name", "Patient Jane Doe")
                patient_name = " ".join(str(raw_name).split())[:120] or "Patient"
                try:
                    age = int(payload.get("age", 74))
                except (TypeError, ValueError):
                    age = 74
                age = max(0, min(120, age))
                sbar = self.engine.generate_sbar_note(audit_result, patient_name, age)
                self._send_json({"sbar": sbar})
                return

            self._send_text("Endpoint not found", 404)
        except Exception as exc:  # keep the demo server alive on malformed input
            self.log_error("Unhandled API error on %s: %s", path, exc)
            self._send_json({"error": "Internal server error"}, 500)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[{self.log_date_time_string()}] {fmt % args}\n")


def run_server(port: int = 8080, host: str = "0.0.0.0") -> None:
    try:
        httpd = PharmaGuardHTTPServer((host, port), PharmaGuardHandler)
    except OSError as exc:
        print(f"Could not bind to {host}:{port} — {exc}", file=sys.stderr)
        print("Is another server already running on this port?", file=sys.stderr)
        raise SystemExit(1)
    display_host = "localhost" if host in ("0.0.0.0", "::") else host
    print("============================================================")
    print(f"  PharmaGuard AI listening at http://{display_host}:{port}")
    print(f"  Knowledge base: {KNOWLEDGE_BASE_META['drug_count']} drugs, "
          f"{KNOWLEDGE_BASE_META['rule_count']} rules")
    print("  Zero external pip dependencies. Press Ctrl+C to stop.")
    print("============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        httpd.server_close()


if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", "8080"))
    except ValueError:
        port = 8080
    host = os.environ.get("HOST", "0.0.0.0")
    if len(sys.argv) > 1 and sys.argv[1] in ("--port", "-p") and len(sys.argv) > 2:
        port = int(sys.argv[2])
    if "--host" in sys.argv:
        try:
            host = sys.argv[sys.argv.index("--host") + 1]
        except IndexError:
            pass
    run_server(port=port, host=host)
