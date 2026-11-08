"""
Lightweight, multi-threaded Web Server and REST API for System Design Agent.
Built with Python standard library (http.server.ThreadingHTTPServer) for zero-dependency reliability.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
import sys
import threading
import time
import urllib.parse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional

from system_design_agent.config import AgentConfig
from system_design_agent.llm import get_llm_client
from system_design_agent.models.spec import SystemDesignSpec
from system_design_agent.pipeline.orchestrator import PipelineOrchestrator
from system_design_agent.pipeline.state import PipelineStage
from system_design_agent.storage.db import SpecRepository

logger = logging.getLogger("system_design_agent.web")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


class DesignAgentHTTPHandler(SimpleHTTPRequestHandler):
    config: AgentConfig = AgentConfig()
    repo: SpecRepository = SpecRepository()

    def do_OPTIONS(self) -> None:
        """Handle CORS pre-flight requests."""
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_cors_headers()
        self.end_headers()

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send_json(self, status: int, data: Any) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(payload)

    def _send_error(self, status: int, message: str) -> None:
        self._send_json(status, {"error": message, "status": status})

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Root: serve index.html
        if path == "/" or path == "/index.html":
            index_path = TEMPLATES_DIR / "index.html"
            if not index_path.is_file():
                self._send_error(404, "Index template not found")
                return
            content = index_path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        # Static assets
        if path.startswith("/static/"):
            filename = path.replace("/static/", "").lstrip("/")
            file_path = STATIC_DIR / filename
            if file_path.is_file():
                content = file_path.read_bytes()
                mime = "application/javascript" if filename.endswith(".js") else "text/css"
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", f"{mime}; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            self._send_error(404, f"Static asset '{filename}' not found")
            return

        # API: Config status
        if path == "/api/config":
            provider = self.config.resolve_provider()
            has_gemini = bool(self.config.gemini_api_key)
            has_anthropic = bool(self.config.anthropic_api_key)
            has_openai = bool(self.config.openai_api_key)
            self._send_json(200, {
                "provider": provider,
                "gemini_model": self.config.gemini_model,
                "anthropic_model": self.config.anthropic_model,
                "openai_model": self.config.openai_model,
                "openai_base_url": self.config.openai_base_url,
                "has_gemini_key": has_gemini,
                "has_anthropic_key": has_anthropic,
                "has_openai_key": has_openai,
                "default_dau": self.config.default_dau,
                "available_providers": ["gemini", "anthropic", "openai", "ollama", "mock"],
                "gemini_models": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro", "gemini-2.0-flash"],
                "claude_models": [
                    "claude-3-opus-20240229",
                    "claude-3-7-sonnet-20250219",
                    "claude-3-5-sonnet-20241022",
                    "claude-3-5-haiku-20241022",
                ],
                "openai_models": [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "o3-mini",
                    "o1",
                    "gpt-4-turbo",
                ],
            })
            return

        # API: List specs
        if path == "/api/specs":
            specs = self.repo.list_specs(limit=50)
            self._send_json(200, {"specs": specs})
            return

        # API: Get single spec
        if path.startswith("/api/specs/") and not path.endswith("/download") and not path.endswith("/markdown"):
            spec_id = path.split("/")[3]
            spec = self.repo.get_by_id(spec_id)
            if not spec:
                self._send_error(404, f"Spec with ID '{spec_id}' not found")
                return
            self._send_json(200, spec)
            return

        # API: Download / view markdown
        if path.startswith("/api/specs/") and (path.endswith("/download") or path.endswith("/markdown")):
            spec_id = path.split("/")[3]
            spec_record = self.repo.get_by_id(spec_id)
            if not spec_record:
                self._send_error(404, f"Spec with ID '{spec_id}' not found")
                return
            md_path = spec_record.get("markdown_path")
            if md_path and Path(md_path).is_file():
                md_bytes = Path(md_path).read_bytes()
            else:
                # Reconstruct from spec json
                data = spec_record.get("spec", {})
                spec_obj = SystemDesignSpec(
                    title=data.get("title", "Specification"),
                    pitch=data.get("pitch", ""),
                    id=data.get("id", spec_id),
                    created_at=data.get("created_at", ""),
                    target_dau=data.get("target_dau", 50000),
                )
                md_bytes = spec_obj.to_markdown().encode("utf-8")

            self.send_response(HTTPStatus.OK)
            disposition = "attachment" if path.endswith("/download") else "inline"
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", f"{disposition}; filename=\"{spec_record['slug']}.md\"")
            self.send_header("Content-Length", str(len(md_bytes)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(md_bytes)
            return

        self._send_error(404, f"Route '{path}' not found")

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Read JSON body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON payload in request body")
            return

        # POST /api/config: update runtime config (Gemini, Anthropic, or OpenAI API keys)
        if path == "/api/config":
            if "gemini_api_key" in payload:
                key = payload["gemini_api_key"].strip()
                if key:
                    self.config.gemini_api_key = key
                    self.config.provider = "gemini"
            if "gemini_model" in payload:
                self.config.gemini_model = payload["gemini_model"].strip()
            if "anthropic_api_key" in payload:
                key = payload["anthropic_api_key"].strip()
                if key:
                    self.config.anthropic_api_key = key
                    self.config.provider = "anthropic"
            if "anthropic_model" in payload:
                self.config.anthropic_model = payload["anthropic_model"].strip()
            if "openai_api_key" in payload:
                key = payload["openai_api_key"].strip()
                if key:
                    self.config.openai_api_key = key
                    self.config.provider = "openai"
            if "openai_model" in payload:
                self.config.openai_model = payload["openai_model"].strip()
            if "openai_base_url" in payload:
                self.config.openai_base_url = payload["openai_base_url"].strip()
            if "provider" in payload:
                self.config.provider = payload["provider"].strip().lower()
            if "default_dau" in payload:
                self.config.default_dau = int(payload["default_dau"])

            self._send_json(200, {
                "message": "Configuration updated successfully",
                "provider": self.config.resolve_provider(),
                "gemini_model": self.config.gemini_model,
                "anthropic_model": self.config.anthropic_model,
                "openai_model": self.config.openai_model,
                "has_gemini_key": bool(self.config.gemini_api_key),
                "has_anthropic_key": bool(self.config.anthropic_api_key),
                "has_openai_key": bool(self.config.openai_api_key),
            })
            return

        # POST /api/generate: run orchestrator with live Server-Sent Events stream
        if path == "/api/generate":
            pitch = payload.get("pitch", "").strip()
            if not pitch:
                self._send_error(400, "Field 'pitch' is required")
                return

            title = payload.get("title") or None
            dau = int(payload.get("dau", self.config.default_dau))
            provider_override = payload.get("provider")
            model_override = payload.get("model")
            gemini_key_override = payload.get("gemini_api_key")
            anthropic_key_override = payload.get("anthropic_api_key")
            openai_key_override = payload.get("openai_api_key")

            # Local config override for this generation job
            resolved_prov = provider_override or self.config.provider or "gemini"
            run_config = AgentConfig(
                provider=resolved_prov,
                gemini_model=model_override if resolved_prov == "gemini" else self.config.gemini_model,
                anthropic_model=model_override if resolved_prov in ("anthropic", "claude") else self.config.anthropic_model,
                openai_model=model_override if resolved_prov == "openai" else self.config.openai_model,
                gemini_api_key=gemini_key_override or self.config.gemini_api_key,
                anthropic_api_key=anthropic_key_override or self.config.anthropic_api_key,
                openai_api_key=openai_key_override or self.config.openai_api_key,
                openai_base_url=self.config.openai_base_url,
                default_dau=dau,
                database_path=self.config.database_path,
                output_dir=self.config.output_dir,
            )

            # Check if client requested SSE stream
            accept = self.headers.get("Accept", "")
            is_stream = "text/event-stream" in accept or payload.get("stream", True)

            if is_stream:
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self._send_cors_headers()
                self.end_headers()

                def send_sse(event_type: str, data: Dict[str, Any]) -> None:
                    try:
                        msg = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
                        self.wfile.write(msg.encode("utf-8"))
                        self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        pass

                def on_stage(stage: PipelineStage, message: str) -> None:
                    send_sse("stage", {
                        "stage": stage.value,
                        "message": message,
                        "timestamp": time.time(),
                    })

                try:
                    client = get_llm_client(run_config)
                    orch = PipelineOrchestrator(config=run_config, client=client, repository=self.repo)
                    spec = orch.run(
                        pitch=pitch,
                        title=title,
                        target_dau=dau,
                        on_stage_update=on_stage,
                    )
                    send_sse("complete", {
                        "id": spec.id,
                        "title": spec.title,
                        "slug": spec.generate_slug(),
                        "target_dau": spec.target_dau,
                        "duration_seconds": spec.duration_seconds,
                        "tokens_used": spec.tokens_used,
                        "markdown": spec.to_markdown(),
                        "validation_report": {
                            "is_valid": spec.validation_report.is_valid,
                            "issues": [
                                {
                                    "severity": i.severity,
                                    "stage": i.stage,
                                    "message": i.message,
                                    "details": i.details,
                                }
                                for i in spec.validation_report.issues
                            ],
                        },
                        "spec": spec.to_dict(),
                    })
                except Exception as e:
                    logger.exception("Pipeline generation failed")
                    send_sse("error", {"message": str(e)})

                return
            else:
                # Synchronous non-streaming response
                try:
                    client = get_llm_client(run_config)
                    orch = PipelineOrchestrator(config=run_config, client=client, repository=self.repo)
                    spec = orch.run(pitch=pitch, title=title, target_dau=dau)
                    self._send_json(200, {
                        "id": spec.id,
                        "title": spec.title,
                        "slug": spec.generate_slug(),
                        "markdown": spec.to_markdown(),
                        "spec": spec.to_dict(),
                    })
                except Exception as e:
                    self._send_error(500, f"Generation failed: {e}")
                return

        self._send_error(404, f"Route '{path}' not found")


def start_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Starts the web dashboard HTTP server."""
    server = ThreadingHTTPServer((host, port), DesignAgentHTTPHandler)
    url = f"http://{host}:{port}"
    print(f"\n🚀 System Design Agent Web UI running at: {url}")
    print(f"👉 Open in browser: {url}\n(Press Ctrl+C to stop)\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
        server.server_close()
