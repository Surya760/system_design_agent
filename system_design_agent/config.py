"""
Configuration management for System Design Agent Pipeline.
Handles environment variables, API keys, model selections, and defaults.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def load_dotenv(dotenv_path: Optional[Path] = None) -> None:
    """Minimal standard-library .env loader so external deps aren't mandatory."""
    path = dotenv_path or Path(".env")
    if not path.is_file():
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass


load_dotenv()


@dataclass
class AgentConfig:
    """Global configuration for the agent pipeline."""
    # LLM Provider settings: 'gemini', 'openai', 'ollama', or 'mock'
    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "").lower())
    
    # Model names
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.1:8b"))
    anthropic_model: str = field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"))
    
    # API Keys & Endpoints
    gemini_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"))
    anthropic_base_url: str = field(default_factory=lambda: os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1"))

    # Pipeline tuning
    temperature: float = 0.2
    max_tokens: int = 4096
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    timeout_seconds: float = 90.0

    # Storage paths
    database_path: Path = field(default_factory=lambda: Path("specs.db"))
    output_dir: Path = field(default_factory=lambda: Path("specs"))

    # Default Scale Baseline
    default_dau: int = 50_000

    def resolve_provider(self) -> str:
        """Auto-detect provider if not explicitly declared."""
        if self.provider:
            return self.provider
        if self.gemini_api_key:
            return "gemini"
        if self.anthropic_api_key:
            return "anthropic"
        if self.openai_api_key:
            return "openai"
        return "mock"
