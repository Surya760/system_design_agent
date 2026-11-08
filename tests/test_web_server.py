"""
Unit tests for the Web UI Server and REST API (in-memory mock socket).
Zero network socket bindings required for clean sandboxed execution.
"""
import io
import json
import unittest
from unittest.mock import MagicMock

from system_design_agent.config import AgentConfig
from system_design_agent.web.server import DesignAgentHTTPHandler


class MockSocket:
    def __init__(self, data: bytes = b""):
        self.rfile = io.BytesIO(data)
        self.output = io.BytesIO()

    def makefile(self, mode: str, bufsize: int = -1):
        if "r" in mode:
            return self.rfile
        return self.output

    def sendall(self, data: bytes):
        self.output.write(data)

    def send(self, data: bytes):
        self.output.write(data)
        return len(data)


class TestWebServer(unittest.TestCase):
    def setUp(self):
        DesignAgentHTTPHandler.config = AgentConfig(provider="mock")

    def _call_handler(self, method: str, path: str, body: dict = None, headers: dict = None) -> tuple[int, dict, bytes]:
        req_headers = headers or {}
        body_bytes = b""
        if body is not None:
            body_bytes = json.dumps(body).encode("utf-8")
            req_headers["Content-Length"] = str(len(body_bytes))
            req_headers["Content-Type"] = "application/json"

        header_lines = [f"{method} {path} HTTP/1.1", "Host: localhost"]
        for k, v in req_headers.items():
            header_lines.append(f"{k}: {v}")
        raw_request = "\r\n".join(header_lines).encode("utf-8") + b"\r\n\r\n" + body_bytes

        mock_sock = MockSocket(raw_request)
        client_address = ("127.0.0.1", 12345)

        # Instantiate handler without running server loop
        handler = DesignAgentHTTPHandler(mock_sock, client_address, None)
        
        # Parse output from handler's output buffer
        output = mock_sock.output.getvalue()
        parts = output.split(b"\r\n\r\n", 1)
        header_part = parts[0].decode("utf-8")
        body_part = parts[1] if len(parts) > 1 else b""
        
        status_line = header_part.splitlines()[0]
        status_code = int(status_line.split()[1])
        
        return status_code, {}, body_part

    def test_get_root_html(self):
        status, _, body = self._call_handler("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"System Design Agent", body)

    def test_get_static_css(self):
        status, _, body = self._call_handler("GET", "/static/style.css")
        self.assertEqual(status, 200)
        self.assertIn(b":root", body)

    def test_get_static_js(self):
        status, _, body = self._call_handler("GET", "/static/app.js")
        self.assertEqual(status, 200)
        self.assertIn(b"mermaid.initialize", body)

    def test_get_api_config(self):
        status, _, body = self._call_handler("GET", "/api/config")
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertIn("provider", data)
        self.assertIn("gemini_models", data)

    def test_get_api_specs(self):
        status, _, body = self._call_handler("GET", "/api/specs")
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertIn("specs", data)
        self.assertIsInstance(data["specs"], list)

    def test_post_api_config(self):
        update_payload = {
            "gemini_api_key": "test_gemini_key_123",
            "gemini_model": "gemini-2.5-pro",
            "default_dau": 75000,
        }
        status, _, body = self._call_handler("POST", "/api/config", body=update_payload)
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(data["gemini_model"], "gemini-2.5-pro")
        self.assertTrue(data["has_gemini_key"])


if __name__ == "__main__":
    unittest.main()
