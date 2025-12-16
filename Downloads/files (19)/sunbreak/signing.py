"""
SunBreak signing utilities: canonicalization, HMAC & ECDSA helpers

This module provides minimal, well-documented helpers used by the reference
implementation. For production use, adapt canonicalization to RFC 8785 (JCS)
and ensure proper key management.
"""
from __future__ import annotations

import json
import base64
import hashlib
import hmac
from typing import Any, Dict

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature,
    decode_dss_signature,
)
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.serialization import load_pem_private_key


def canonicalize_envelope(envelope: Dict[str, Any]) -> bytes:
    """Produce a deterministic canonical JSON representation.

    This implementation uses sorted keys and compact separators. For strict
    interoperability consider using RFC 8785 (JCS).
    """
    return json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def compute_payload_hash(payload: Dict[str, Any]) -> str:
    """Compute hex-encoded SHA-256 of the canonicalized payload object."""
    payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload_bytes).hexdigest()


def sign_hmac(secret: bytes, envelope: Dict[str, Any]) -> str:
    """Sign envelope using HMAC-SHA256 and return base64 signature."""
    canonical = canonicalize_envelope(envelope)
    mac = hmac.new(secret, canonical, hashlib.sha256).digest()
    return base64.b64encode(mac).decode("ascii")


def verify_hmac(secret: bytes, envelope: Dict[str, Any], sig_b64: str) -> bool:
    expected = sign_hmac(secret, envelope)
    # Use compare_digest to avoid timing attacks
    return hmac.compare_digest(expected, sig_b64)


def sign_ecdsa(private_key: ec.EllipticCurvePrivateKey, envelope: Dict[str, Any]) -> str:
    canonical = canonicalize_envelope(envelope)
    digest = hashlib.sha256(canonical).digest()
    signature = private_key.sign(digest, ec.ECDSA(hashes.SHA256()))
    # signature is DER-encoded; base64 for transport
    return base64.b64encode(signature).decode("ascii")


def verify_ecdsa(public_pem: bytes, envelope: Dict[str, Any], sig_b64: str) -> bool:
    try:
        public_key = load_pem_public_key(public_pem)
        canonical = canonicalize_envelope(envelope)
        digest = hashlib.sha256(canonical).digest()
        signature = base64.b64decode(sig_b64)
        public_key.verify(signature, digest, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False


def sign_ecdsa_pem(private_pem: bytes, envelope: Dict[str, Any]) -> str:
    """Convenience: load private PEM and sign envelope, return base64 sig."""
    priv = load_pem_private_key(private_pem, password=None)
    return sign_ecdsa(priv, envelope)
