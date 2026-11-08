"""
Unit tests for OpenAICompatClient (GPT-4o, o1, o3-mini).
"""
import json
import unittest
from unittest.mock import MagicMock, patch

from system_design_agent.llm.base import LLMResponse
from system_design_agent.llm.openai_compat import OpenAICompatClient


class TestOpenAICompatClient(unittest.TestCase):
    def test_missing_api_key_raises_value_error(self):
        with self.assertRaises(ValueError):
            OpenAICompatClient(api_key="", base_url="https://api.openai.com/v1")

    def test_local_endpoint_allows_dummy_key(self):
        client = OpenAICompatClient(api_key="", base_url="http://localhost:11434/v1")
        self.assertEqual(client.api_key, "dummy-key-for-local")

    @patch("urllib.request.urlopen")
    def test_successful_gpt4o_generation(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        response_data = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "### 2. High-Level Design (HLD)\n\n#### Architectural Paradigm..."
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 1200,
                "completion_tokens": 600,
                "total_tokens": 1800
            }
        }
        mock_response.read.return_value = json.dumps(response_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = OpenAICompatClient(api_key="sk-test-openai-key", model="gpt-4o")
        resp = client.generate(
            prompt="Design a real-time messaging platform",
            system_prompt="You are a Principal Architect",
            temperature=0.2,
            max_tokens=4096,
        )

        self.assertIsInstance(resp, LLMResponse)
        self.assertIn("High-Level Design", resp.content)
        self.assertEqual(resp.model, "gpt-4o")
        self.assertEqual(resp.provider, "openai")
        self.assertEqual(resp.tokens_used, 1800)

        # Check payload
        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "gpt-4o")
        self.assertEqual(payload["temperature"], 0.2)
        self.assertEqual(payload["max_tokens"], 4096)
        self.assertEqual(payload["messages"][0]["role"], "system")

    @patch("urllib.request.urlopen")
    def test_reasoning_models_o1_o3_parameter_adaptation(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        response_data = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "### 3. Low-Level Design (LLD)..."
                    }
                }
            ],
            "usage": {"total_tokens": 2500}
        }
        mock_response.read.return_value = json.dumps(response_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test with o3-mini
        client = OpenAICompatClient(api_key="sk-test-key", model="o3-mini")
        resp = client.generate(
            prompt="Design schema",
            system_prompt="Architect persona",
            max_tokens=4096,
        )

        self.assertEqual(resp.tokens_used, 2500)
        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode("utf-8"))
        
        # Verify o-series parameter rules
        self.assertIn("max_completion_tokens", payload)
        self.assertNotIn("temperature", payload)
        self.assertEqual(payload["messages"][0]["role"], "developer")


if __name__ == "__main__":
    unittest.main()
