"""
SQLite database storage layer for persisting generation sessions and specifications.
"""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional

from system_design_agent.models.spec import SystemDesignSpec


class SpecRepository:
    def __init__(self, db_path: Path = Path("specs.db")):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS specifications (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    pitch TEXT NOT NULL,
                    target_dau INTEGER NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    duration_seconds REAL NOT NULL,
                    is_valid INTEGER NOT NULL,
                    markdown_path TEXT,
                    created_at TEXT NOT NULL,
                    spec_json TEXT NOT NULL
                );
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_spec_created_at ON specifications (created_at DESC);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_spec_slug ON specifications (slug);
            """)
            conn.commit()

    def save(self, spec: SystemDesignSpec, markdown_path: Optional[str] = None) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO specifications (
                    id, title, slug, pitch, target_dau, tokens_used,
                    duration_seconds, is_valid, markdown_path, created_at, spec_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                spec.id,
                spec.title,
                spec.generate_slug(),
                spec.pitch,
                spec.target_dau,
                spec.tokens_used,
                spec.duration_seconds,
                1 if spec.validation_report.is_valid else 0,
                markdown_path,
                spec.created_at,
                json.dumps(spec.to_dict()),
            ))
            conn.commit()

    def list_specs(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, slug, target_dau, tokens_used, duration_seconds, is_valid, markdown_path, created_at
                FROM specifications
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, spec_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM specifications WHERE id = ?", (spec_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data["spec"] = json.loads(data["spec_json"])
                return data
            return None
