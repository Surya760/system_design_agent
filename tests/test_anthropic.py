"""
Unit tests for AnthropicClient (Claude Opus / Sonnet).
"""
import json
import unittest
from unittest.mock import MagicMock, patch

from system_design_agent.llm.anthropic import AnthropicClient
from system_design_agent.llm.base import LLMResponse


class TestAnthropicClient(unittest.TestCase):
    def test_missing_api_key_raises_value_error(self):
        with self.assertRaises(ValueError):
            AnthropicClient(api_key="")

    @patch("urllib.request.urlopen")
    def test_successful_claude_opus_generation(self, mock_urlopen):
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status = 200
        response_data = {
            "id": "msg_01X9",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "### 1. Requirements & Core Assumptions\n\n#### Functional Requirements..."
                }
            ],
            "model": "claude-3-opus-20240229",
            "usage": {
                "input_tokens": 1500,
                "output_tokens": 850
            }
        }
        mock_response.read.return_value = json.dumps(response_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = AnthropicClient(api_key="sk-ant-test-key", model="claude-3-opus-20240229")
        resp = client.generate(
            prompt="Pitch: High-concurrency flash sale engine",
            system_prompt="You are a Principal Systems Architect",
            temperature=0.2,
        )

        self.assertIsInstance(resp, LLMResponse)
        self.assertIn("Requirements", resp.content)
        self.assertEqual(resp.model, "claude-3-opus-20240229")
        self.assertEqual(resp.provider, "anthropic")
        self.assertEqual(resp.tokens_used, 2350)

        # Verify request structure
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        self.assertEqual(req.full_url, "https://api.anthropic.com/v1/messages")
        self.assertEqual(req.headers.get("X-api-key"), "sk-ant-test-key")
        self.assertEqual(req.headers.get("Anthropic-version"), "2023-06-01")

        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "claude-3-opus-20240229")
        self.assertEqual(payload["system"], "You are a Principal Systems Architect")
        self.assertEqual(payload["messages"][0]["content"], "Pitch: High-concurrency flash sale engine")


if __name__ == "__main__":
    unittest.main()
