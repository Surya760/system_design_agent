"""
Integration tests for PipelineOrchestrator and end-to-end execution.
"""
from pathlib import Path
import tempfile
import unittest

from system_design_agent.config import AgentConfig
from system_design_agent.llm.mock import MockLLMClient
from system_design_agent.pipeline.orchestrator import PipelineOrchestrator
from system_design_agent.storage.db import SpecRepository


class TestPipelineOrchestrator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_specs.db"
        self.output_dir = Path(self.temp_dir.name) / "specs"
        self.config = AgentConfig(
            provider="mock",
            database_path=self.db_path,
            output_dir=self.output_dir,
            default_dau=50_000,
        )
        self.client = MockLLMClient()
        self.repo = SpecRepository(self.db_path)
        self.orchestrator = PipelineOrchestrator(
            config=self.config,
            client=self.client,
            repository=self.repo,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_full_pipeline_run(self):
        pitch = "Real-time collaborative code editor with conflict resolution, cursor sharing, and live chat."
        output_file = self.output_dir / "collab-editor.md"

        spec = self.orchestrator.run(
            pitch=pitch,
            title="Real-Time Collaborative Code Editor",
            target_dau=50_000,
            output_file=output_file,
        )

        self.assertIsNotNone(spec)
        self.assertEqual(spec.title, "Real-Time Collaborative Code Editor")
        self.assertEqual(spec.target_dau, 50_000)
        self.assertTrue(output_file.is_file())

        content = output_file.read_text(encoding="utf-8")
        self.assertIn("## 1. Requirements & Core Assumptions", content)
        self.assertIn("## 2. High-Level Design (HLD)", content)
        self.assertIn("## 3. Low-Level Design (LLD)", content)
        self.assertIn("## 4. Resilience, Concurrency & Security", content)
        self.assertIn("## 5. Developer Action Plan & Scaffolding", content)
        self.assertIn("```mermaid", content)
        self.assertIn("CREATE TABLE", content)

        # Check repository persistence
        saved_list = self.repo.list_specs()
        self.assertEqual(len(saved_list), 1)
        self.assertEqual(saved_list[0]["slug"], spec.generate_slug())

        # Check validation
        self.assertTrue(spec.validation_report.is_valid)


if __name__ == "__main__":
    unittest.main()
