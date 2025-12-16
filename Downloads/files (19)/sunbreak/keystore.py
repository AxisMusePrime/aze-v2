"""Key management helpers for SunBreak reference implementation.

Provides utilities to generate and load ECDSA P-256 test keys into
`sunbreak/keys/`. In production, replace with a secure KMS-backed store.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


PKG_DIR = Path(__file__).resolve().parent
KEYS_DIR = PKG_DIR / "keys"
KEYS_DIR.mkdir(parents=True, exist_ok=True)


def _priv_path(keyid: str) -> Path:
    return KEYS_DIR / f"{keyid}_private.pem"


def _pub_path(keyid: str) -> Path:
    return KEYS_DIR / f"{keyid}_public.pem"


def generate_ecdsa_keypair(keyid: str) -> Dict[str, bytes]:
    """Generate and persist an ECDSA P-256 keypair for tests.

    Returns dict with `private_pem` and `public_pem` (bytes).
    If files already exist they will be returned unchanged.
    """
    priv_p = _priv_path(keyid)
    pub_p = _pub_path(keyid)

    if priv_p.exists() and pub_p.exists():
        return {"private_pem": priv_p.read_bytes(), "public_pem": pub_p.read_bytes()}

    # Generate new key
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    priv_p.write_bytes(private_pem)
    pub_p.write_bytes(public_pem)

    return {"private_pem": private_pem, "public_pem": public_pem}


def load_public_key_pem(keyid: str) -> bytes:
    p = _pub_path(keyid)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return p.read_bytes()


def load_private_key_pem(keyid: str) -> bytes:
    p = _priv_path(keyid)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return p.read_bytes()


def ensure_test_keys():
    """Ensure a default test keypair exists and return keyids mapping."""
    test_keyid = "test-ecdsa-1"
    pair = generate_ecdsa_keypair(test_keyid)
    return {test_keyid: pair}


if __name__ == "__main__":
    pair = generate_ecdsa_keypair("test-ecdsa-1")
    print("Generated test keypair with id=test-ecdsa-1")
