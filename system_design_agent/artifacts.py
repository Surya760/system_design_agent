"""Export a design specification as a small, shareable artifact bundle."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

from system_design_agent.models.spec import SystemDesignSpec


def _mermaid_blocks(markdown: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"```mermaid\s*\n([\s\S]*?)```", markdown, re.IGNORECASE)]


def _mermaid_blocks_with_headings(markdown: str) -> list[tuple[str, str]]:
    blocks = []
    for match in re.finditer(r"```mermaid\s*\n([\s\S]*?)```", markdown, re.IGNORECASE):
        preceding = markdown[:match.start()].splitlines()
        headings = [line.lstrip("# ").strip().lower() for line in preceding if line.startswith("#")]
        blocks.append((headings[-1] if headings else "", match.group(1).strip()))
    return blocks


def _first_block(markdown: str, language: str) -> str:
    pattern = rf"```{re.escape(language)}\s*\n([\s\S]*?)```"
    match = re.search(pattern, markdown, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _section(markdown: str, heading: str) -> str:
    pattern = rf"^#{2,4}\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^#{2,4}\s+|\Z)"
    match = re.search(pattern, markdown, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def _write_files(folder: Path, files: Dict[str, str]) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        if content.strip():
            (folder / name).write_text(content.rstrip() + "\n", encoding="utf-8")
    return folder


def write_design_bundle(spec: SystemDesignSpec, folder: Path) -> Path:
    """Write design markdown, Mermaid source files, and API documents when present."""
    hld_diagrams = _mermaid_blocks_with_headings(spec.hld.raw_markdown)
    lld_diagrams = _mermaid_blocks(spec.lld.raw_markdown)
    architecture = next((block for heading, block in hld_diagrams if block.startswith(("graph", "flowchart")) and "deploy" not in heading), "")
    deployment = next((block for heading, block in hld_diagrams if "deploy" in heading), "")
    erd = next((block for block in lld_diagrams if block.startswith("erDiagram")), "")
    sequence = next((block for block in lld_diagrams if block.startswith("sequenceDiagram")), "")
    api_contract = _section(spec.lld.raw_markdown, "Human-Readable API Contract")
    if not api_contract:
        api_contract = _section(spec.lld.raw_markdown, "API Contracts")
    if not api_contract:
        api_contract = _section(spec.lld.raw_markdown, "API Contract")
    openapi = _first_block(spec.lld.raw_markdown, "yaml")

    files = {
        "system-design.md": spec.to_markdown(),
        "architecture.mmd": architecture,
        "deployment.mmd": deployment,
        "database-erd.mmd": erd,
        "sequence.mmd": sequence,
        "openapi.yaml": openapi,
        "API_CONTRACT.md": f"# API Contract: {spec.title}\n\n{api_contract}" if api_contract else "",
        "README.md": (
            f"# {spec.title} design artifacts\n\n"
            "Start with [system-design.md](system-design.md). Mermaid source diagrams and API contract files are included when generated.\n"
        ),
    }
    return _write_files(folder, files)
