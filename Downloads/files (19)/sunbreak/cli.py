"""SunBreak CLI helper: sign and submit envelopes"""
from __future__ import annotations

import json
import sys
import argparse
import requests

from .signing import sign_hmac, canonicalize_envelope, sign_ecdsa_pem
from .keystore import generate_ecdsa_keypair, load_private_key_pem


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    parser = argparse.ArgumentParser(description="SunBreak CLI: sign and submit envelopes")
    parser.add_argument("--envelope", required=True, help="Path to JSON envelope file")
    parser.add_argument("--api-key-id", required=True, help="API key id (X-API-Key)")
    parser.add_argument("--secret", required=True, help="HMAC secret")
    parser.add_argument("--url", required=True, help="Submit URL e.g. https://api.example.com/sunbreak/v1/submit")
    args = parser.parse_args(argv)

    envelope = load_json(args.envelope)
    if args.scheme and args.scheme.lower().startswith("ecdsa"):
        # use provided private PEM path or generate demo key
        if args.secret == "__generate_test_key__":
            pair = generate_ecdsa_keypair(args.api_key_id)
            private_pem = pair["private_pem"]
        else:
            private_pem = args.secret.encode() if args.secret.strip().startswith("-----") else load_private_key_pem(args.api_key_id)
        sig = sign_ecdsa_pem(private_pem, envelope)
    else:
        sig = sign_hmac(args.secret.encode(), envelope)

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": args.api_key_id,
        "X-SunBreak-Signature": f"scheme=HMAC-SHA256;keyid={args.api_key_id};sig={sig}",
        "X-SunBreak-Timestamp": envelope.get("timestamp"),
        "X-SunBreak-Nonce": envelope.get("nonce"),
    }

    resp = requests.post(args.url, headers=headers, json=envelope)
    print(f"HTTP {resp.status_code}")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)


if __name__ == "__main__":
    main()
