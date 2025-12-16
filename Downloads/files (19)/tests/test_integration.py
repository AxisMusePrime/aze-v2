import json
import time
from datetime import datetime

from datavalid_api import app, SUNBREAK_SECRETS
from sunbreak.signing import sign_hmac, compute_payload_hash


def test_sunbreak_end_to_end():
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Build envelope with inline dataset
        env = {
            "version": "v1",
            "message_id": "int-test-1",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ttl_seconds": 300,
            "nonce": f"nint-{int(time.time())}",
            "sender_id": "integration-test-org",
            "recipient_id": "datavalid",
            "payload": {
                "request_type": "validate",
                "dataset_name": "integration-sample",
                "dataset": {
                    "email": ["email", ["alice@example.com", "bob@example.com", None]],
                    "name": ["name", ["Alice", "B"]],
                },
            },
        }
        env["payload_hash"] = compute_payload_hash(env["payload"])
        secret = SUNBREAK_SECRETS["demo-key-123"]
        sig = sign_hmac(secret, env)
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": "demo-key-123",
            "X-SunBreak-Signature": f"scheme=HMAC-SHA256;keyid=demo-key-123;sig={sig}",
            "X-SunBreak-Timestamp": env["timestamp"],
            "X-SunBreak-Nonce": env["nonce"],
        }

        rv = client.post("/sunbreak/v1/submit", data=json.dumps(env), headers=headers)
        assert rv.status_code == 202
        body = rv.get_json()
        assert body.get("receipt_id")
        # validation_summary should be present for inline validate payloads
        assert "validation_summary" in body
        vs = body["validation_summary"]
        assert "overall_quality" in vs