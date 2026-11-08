"""
Unit tests for the SSL Context resolver.
"""
import ssl
import unittest

from system_design_agent.llm.ssl_context import get_ssl_context


class TestSSLContext(unittest.TestCase):
    def test_get_ssl_context_returns_valid_context(self):
        ctx = get_ssl_context()
        self.assertIsInstance(ctx, ssl.SSLContext)
        # Should have CA certs loaded on this machine
        certs = ctx.get_ca_certs()
        self.assertGreater(len(certs), 0, "Expected at least 1 root CA certificate in context")


if __name__ == "__main__":
    unittest.main()
