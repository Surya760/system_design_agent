"""Load the bundled System Design Starter skill and task-specific guides."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable

SKILL_ROOT = Path(__file__).resolve().parents[1] / "skills" / "system-design-starter"


@lru_cache(maxsize=8)
def _read(relative_path: str) -> str:
    path = (SKILL_ROOT / relative_path).resolve()
    if SKILL_ROOT.resolve() not in path.parents:
        raise ValueError("Skill reference must stay inside the bundled skill directory")
    return path.read_text(encoding="utf-8")


def load_skill_context(references: Iterable[str] = ()) -> str:
    """Return core skill instructions plus only the guides relevant to one stage."""
    sections = ["## System Design Starter skill", _read("SKILL.md")]
    for reference in references:
        if "/" in reference or ".." in reference:
            raise ValueError(f"Invalid skill reference name: {reference}")
        sections.extend([f"## Relevant guide: {reference}", _read(f"references/{reference}.md")])
    return "\n\n".join(sections)
