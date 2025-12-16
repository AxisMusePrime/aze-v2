import json
import base64
import time
from datetime import datetime

import pytest

from datavalid_api import app, SUNBREAK_SECRETS
from sunbreak.signing import sign_hmac, compute_payload_hash


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_envelope():
    env = {
        "version": "v1",
        "message_id": "test-msg-1",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ttl_seconds": 300,
        "nonce": f"n-{int(time.time())}",
        "sender_id": "test-org",
        "recipient_id": "datavalid",
        "payload": {"request_type": "validate", "dataset_ref": "s3://bucket/data.csv"},
    }
    env["payload_hash"] = compute_payload_hash(env["payload"])
    return env


def test_hmac_sign_and_submit(client):
    env = make_envelope()
    # compute payload hash
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
    assert body.get("status") == "accepted"
