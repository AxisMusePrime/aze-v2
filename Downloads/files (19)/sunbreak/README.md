# SunBreak Reference Package

SunBreak provides a small reference implementation for the SunBreak protocol (JSON-over-HTTPS message exchange with signing and audit receipts).

Usage (examples):

- Generate test ECDSA keys (for development only):

```bash
python -m sunbreak.keystore
```

- Sign and submit an envelope (HMAC example):

```bash
python -m sunbreak.cli --envelope ./envelope.json --api-key-id demo-key-123 --secret demo-secret-abc123 --url https://localhost:5000/sunbreak/v1/submit
```

Notes:
- The `keystore` module will generate P-256 test keys under `sunbreak/keys/` if missing. Do not use test keys in production.
- The package includes signing helpers (HMAC and ECDSA). For interoperability use RFC 8785 (JCS) for canonical JSON in production.
# SunBreak — Reference Implementation (DataValid)

This package provides a minimal, reference implementation of the SunBreak protocol used by DataValid for secure, signed submissions and tamper-evident receipts.

Contents
- `signing.py`: canonicalization, HMAC and ECDSA helpers
- `keystore.py`: simple test key generation and loading utilities (for local development)
- `cli.py`: CLI helper to sign and submit envelopes
- `keys/`: generated test keys (created on first use)

Getting started
1. Install requirements: `python3 -m pip install -r datavalid_requirements.txt`
2. Generate test keys (created automatically on first run) or call `generate_ecdsa_keypair` from `keystore`.
3. Use `sunbreak/cli.py` to sign and submit envelopes.

Notes
- The keystore is for local testing only. Do not use generated keys in production.
- For production use a proper KMS (AWS KMS, Google KMS, Azure Key Vault).
