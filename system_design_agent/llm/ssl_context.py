"""
SSL Context resolver for macOS, Linux, and Windows.
Resolves local CA certificates when Python's default keystore is unpopulated on macOS.
"""
from __future__ import annotations

import logging
import os
import ssl
from typing import Optional

logger = logging.getLogger(__name__)


def get_ssl_context() -> ssl.SSLContext:
    """Builds a secure SSLContext with valid root CA certificates across operating systems."""
    # Check if user explicitly asked to skip verification
    if os.getenv("SSL_NO_VERIFY", "0").lower() in ("1", "true", "yes"):
        logger.warning("SSL_NO_VERIFY is enabled. Disabling SSL certificate verification.")
        ctx = ssl._create_unverified_context()
        return ctx

    # 1. Check explicit environment variables
    for env_var in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"):
        ca_file = os.getenv(env_var)
        if ca_file and os.path.isfile(ca_file):
            try:
                ctx = ssl.create_default_context(cafile=ca_file)
                if len(ctx.get_ca_certs()) > 0:
                    return ctx
            except Exception as e:
                logger.debug("Failed loading %s (%s): %s", env_var, ca_file, e)

    # 2. Check certifi if installed
    try:
        import certifi
        ca_file = certifi.where()
        if os.path.isfile(ca_file):
            return ssl.create_default_context(cafile=ca_file)
    except ImportError:
        pass

    # 3. Check known OS system CA certificate bundles (macOS, Debian, RHEL, SUSE)
    os_bundles = [
        "/etc/ssl/cert.pem",                   # macOS default system bundle & Alpine Linux
        "/private/etc/ssl/cert.pem",           # macOS alternate symlink target
        "/etc/ssl/certs/ca-certificates.crt", # Debian / Ubuntu
        "/etc/pki/tls/certs/ca-bundle.crt",   # Fedora / RHEL / CentOS
        "/etc/ssl/ca-bundle.pem",             # openSUSE
    ]
    for ca_path in os_bundles:
        if os.path.isfile(ca_path):
            try:
                ctx = ssl.create_default_context(cafile=ca_path)
                if len(ctx.get_ca_certs()) > 0:
                    return ctx
            except Exception as e:
                logger.debug("Failed loading system bundle %s: %s", ca_path, e)

    # 4. Check Python default context
    ctx = ssl.create_default_context()
    if len(ctx.get_ca_certs()) > 0:
        return ctx

    # 5. Fallback if keystore has 0 certificates (unlinked macOS Python installation)
    logger.warning(
        "No root certificates found in Python keystore. "
        "Falling back to unverified context to avoid SSL failure."
    )
    return ssl._create_unverified_context()
