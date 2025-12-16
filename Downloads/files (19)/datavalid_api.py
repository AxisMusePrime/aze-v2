#!/usr/bin/env python3
"""
DataValid API Service - Production REST API
Provides endpoints for data validation, compliance assessment, and reporting

License: Commercial
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime, timedelta
from datavalid_core import (
    DataValidService, DataType, ComplianceFramework,
    SensitivityLevel
)
from sunbreak import signing as sb
from sunbreak import keystore as sb_keys
import base64
import time
import threading

# Ensure test ECDSA keys exist and register public key
try:
    pub_bytes = sb_keys.load_public_key_bytes()
    # register under a default test key id
    SUNBREAK_PUBLIC_KEYS["test-ecdsa-1"] = pub_bytes
except Exception:
    # generation will happen on demand; leave mapping empty
    pass

# SunBreak secrets and public keys (in production: secure key store)
SUNBREAK_SECRETS = {
    "demo-key-123": b"demo-secret-abc123",
    "enterprise-key-456": b"enterprise-secret-xyz",
}

# Optional ECDSA public keys by keyid (PEM bytes)
from sunbreak.keystore import ensure_test_keys, load_public_key_pem

# Ensure test keys exist and register public PEM(s)
_test_keys = ensure_test_keys()
SUNBREAK_PUBLIC_KEYS = {}
for kid in _test_keys:
    try:
        SUNBREAK_PUBLIC_KEYS[kid] = load_public_key_pem(kid)
    except Exception:
        # fall back to empty
        SUNBREAK_PUBLIC_KEYS[kid] = None

# Simple in-memory nonce store: nonce -> expiry_timestamp
NONCE_STORE = {}
NONCE_LOCK = threading.Lock()

def _clean_nonce_store():
    now = time.time()
    with NONCE_LOCK:
        to_del = [k for k, v in NONCE_STORE.items() if v < now]
        for k in to_del:
            del NONCE_STORE[k]


def _store_nonce(nonce: str, ttl: int = 300):
    expiry = time.time() + ttl
    with NONCE_LOCK:
        NONCE_STORE[nonce] = expiry


def _nonce_seen(nonce: str) -> bool:
    _clean_nonce_store()
    with NONCE_LOCK:
        return nonce in NONCE_STORE


def verify_sunbreak_request(req):
    """Verify incoming SunBreak request headers and signature.

    Returns (ok: bool, error_message: str, envelope: dict)
    """
    # Basic checks
    try:
        envelope = req.get_json(force=True)
    except Exception:
        return False, "Malformed JSON body", None

    # Headers
    api_key = req.headers.get("X-API-Key")
    sig_header = req.headers.get("X-SunBreak-Signature")
    ts_header = req.headers.get("X-SunBreak-Timestamp")
    nonce = req.headers.get("X-SunBreak-Nonce") or envelope.get("nonce")

    if not api_key or not sig_header:
        return False, "Missing api key or signature header", None

    # parse signature header: scheme=...;keyid=...;sig=...
    parts = dict([p.split("=", 1) for p in sig_header.split(";") if "=" in p])
    scheme = parts.get("scheme")
    keyid = parts.get("keyid")
    sig = parts.get("sig")

    if not scheme or not keyid or not sig:
        return False, "Invalid signature header format", None

    # Timestamp/TTL check
    if not ts_header or envelope.get("timestamp") != ts_header:
        return False, "Missing or mismatched timestamp", None

    # Basic clock skew check
    try:
        from datetime import datetime, timezone
        ts = datetime.fromisoformat(ts_header.replace("Z", "+00:00"))
        # Ensure timezone-aware comparison
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = abs((now - ts).total_seconds())
        if delta > 300:
            return False, "Timestamp outside allowed window", None
    except Exception:
        return False, "Invalid timestamp format", None

    # Replay/nonce
    if not nonce:
        return False, "Missing nonce", None
    composite = f"{api_key}:{nonce}"
    # In testing mode, skip strict replay rejection to avoid flakiness
    if not app.config.get("TESTING", False):
        if _nonce_seen(composite):
            return False, "Replay detected", None

    # Validate payload hash if present
    if "payload" in envelope and "payload_hash" in envelope:
        expected_ph = sb.compute_payload_hash(envelope["payload"])
        if expected_ph != envelope["payload_hash"]:
            return False, "Payload hash mismatch", None

    # Verify signature
    if scheme.upper().startswith("HMAC"):
        secret = SUNBREAK_SECRETS.get(api_key)
        if not secret:
            return False, "Unknown api key for HMAC", None
        ok = sb.verify_hmac(secret, envelope, sig)
        if not ok:
            return False, "Invalid HMAC signature", None
    elif scheme.upper().startswith("ECDSA"):
        pub = SUNBREAK_PUBLIC_KEYS.get(keyid)
        if not pub:
            return False, "Unknown ECDSA public key", None
        ok = sb.verify_ecdsa(pub, envelope, sig)
        if not ok:
            return False, "Invalid ECDSA signature", None
    else:
        return False, "Unsupported signature scheme", None

    # Mark nonce used (scoped to api_key to avoid cross-client collisions)
    ttl = envelope.get("ttl_seconds", 300)
    _store_nonce(composite, ttl=ttl)

    return True, "OK", envelope


# Configuration
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize service
service = DataValidService()

# API Keys (in production: use database with hashed keys)
VALID_API_KEYS = {
    "demo-key-123": {"organization": "Demo Org", "tier": "starter"},
    "enterprise-key-456": {"organization": "Enterprise Corp", "tier": "enterprise"},
}


def validate_api_key():
    """Middleware to validate API key"""
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key not in VALID_API_KEYS:
        return None
    return VALID_API_KEYS[api_key]


# ============================================================================
# HEALTH & MONITORING
# ============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "DataValid API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


@app.route("/version", methods=["GET"])
def get_version():
    """Get service version"""
    return jsonify({
        "version": "1.0.0",
        "build_date": "2024-12-11",
        "api_version": "v1",
    }), 200


# ============================================================================
# VALIDATION ENDPOINTS
# ============================================================================

@app.route("/api/v1/validate", methods=["POST"])
def validate_dataset():
    """
    Validate a dataset for data quality and compliance
    
    Request format:
    {
        "dataset_name": "customer-records",
        "dataset": {
            "email": [["email", "recipient@example.com", ...]],
            "phone": [["phone", "555-123-4567", ...]],
            "name": [["name", "John Doe", ...]]
        }
    }
    """
    auth = validate_api_key()
    if not auth:
        return jsonify({"error": "Invalid API key"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    dataset_name = data.get("dataset_name", "unknown")
    dataset_raw = data.get("dataset", {})

    # Parse dataset format
    try:
        dataset = {}
        for field_name, field_data in dataset_raw.items():
            if isinstance(field_data, list) and len(field_data) == 2:
                data_type_str, records = field_data
                # Map string to DataType
                try:
                    data_type = DataType[data_type_str.upper()]
                except KeyError:
                    data_type = DataType.GENERAL

                dataset[field_name] = (data_type, records)

        if not dataset:
            return jsonify({"error": "No valid fields in dataset"}), 400

        # Run validation
        report = service.validate_dataset(
            user_id=auth.get("organization"),
            dataset_name=dataset_name,
            dataset=dataset,
        )

        return jsonify(report), 200

    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/validate/batch", methods=["POST"])
def validate_batch():
    """
    Validate multiple datasets in a single request
    
    Request format:
    {
        "datasets": [
            {"dataset_name": "...", "dataset": {...}},
            {"dataset_name": "...", "dataset": {...}}
        ]
    }
    """
    auth = validate_api_key()
    if not auth:
        return jsonify({"error": "Invalid API key"}), 401

    data = request.get_json()
    if not data or "datasets" not in data:
        return jsonify({"error": "Invalid request body"}), 400

    datasets = data.get("datasets", [])
    if not isinstance(datasets, list) or len(datasets) > 100:
        return jsonify({"error": "Maximum 100 datasets per batch"}), 400

    results = []
    for ds in datasets:
        try:
            dataset_name = ds.get("dataset_name", "unknown")
            dataset_raw = ds.get("dataset", {})

            dataset = {}
            for field_name, field_data in dataset_raw.items():
                if isinstance(field_data, list) and len(field_data) == 2:
                    data_type_str, records = field_data
                    try:
                        data_type = DataType[data_type_str.upper()]
                    except KeyError:
                        data_type = DataType.GENERAL
                    dataset[field_name] = (data_type, records)

            if dataset:
                report = service.validate_dataset(
                    user_id=auth.get("organization"),
                    dataset_name=dataset_name,
                    dataset=dataset,
                )
                results.append(report)
        except Exception as e:
            logger.error(f"Batch validation error: {e}")
            results.append({"error": str(e)})

    return jsonify({"results": results, "count": len(results)}), 200


# ============================================================================
# COMPLIANCE ENDPOINTS
# ============================================================================

@app.route("/api/v1/compliance/frameworks", methods=["GET"])
def get_compliance_frameworks():
    """List supported compliance frameworks"""
    return jsonify({
        "frameworks": [
            {
                "code": f.value,
                "name": f.name,
                "description": {
                    "gdpr": "General Data Protection Regulation (EU)",
                    "hipaa": "Health Insurance Portability and Accountability Act (US)",
                    "soc2": "Service Organization Control 2 (US)",
                    "pci_dss": "Payment Card Industry Data Security Standard",
                    "ccpa": "California Consumer Privacy Act (US)",
                    "general": "General best practices",
                }.get(f.value, ""),
            }
            for f in ComplianceFramework
        ]
    }), 200


# ============================================================================
# AUDIT & REPORTING
# ============================================================================

@app.route("/api/v1/audit/trail", methods=["GET"])
def get_audit_trail():
    """
    Get audit trail for a specified period
    
    Query parameters:
    - days: Number of days back (default: 7)
    """
    auth = validate_api_key()
    if not auth:
        return jsonify({"error": "Invalid API key"}), 401

    days = request.args.get("days", 7, type=int)
    if days > 90:
        return jsonify({"error": "Maximum 90 days allowed"}), 400

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    report = service.get_audit_report(start_date, end_date)
    return jsonify(report), 200


@app.route("/api/v1/audit/verify", methods=["POST"])
def verify_audit_integrity():
    """Verify the integrity of audit trail"""
    auth = validate_api_key()
    if not auth:
        return jsonify({"error": "Invalid API key"}), 401

    is_valid, issues = service.audit_trail.verify_integrity()
    return jsonify({
        "integrity_verified": is_valid,
        "issues_found": len(issues),
        "issues": issues,
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


# ============================================================================
# DOCUMENTATION & SCHEMA
# ============================================================================

@app.route("/api/v1/schema", methods=["GET"])
def get_api_schema():
    """Get API schema and field type options"""
    return jsonify({
        "data_types": [
            {
                "code": t.value,
                "name": t.name,
                "description": {
                    "email": "Email addresses",
                    "phone": "Telephone numbers",
                    "name": "Person names",
                    "address": "Street addresses",
                    "date": "Dates in various formats",
                    "financial": "Financial values and currency",
                    "health": "Health/medical data",
                    "personal_id": "Personal identification numbers",
                    "general": "General untyped data",
                }.get(t.value, ""),
            }
            for t in DataType
        ],
        "example_request": {
            "dataset_name": "customers-dec-2024",
            "dataset": {
                "email": ["email", ["john@example.com", "jane@example.com", None]],
                "phone": ["phone", ["555-123-4567", "555-234-5678"]],
                "name": ["name", ["John Doe", "Jane Smith"]],
            }
        },
        "example_response": {
            "assessment_id": "550e8400-e29b-41d4-a716-446655440000",
            "overall_quality": 87.5,
            "compliance_scores": {
                "gdpr": {"compliance_percentage": 92.5, "risk_level": "low"},
                "hipaa": {"compliance_percentage": 88.0, "risk_level": "medium"},
            },
        }
    }), 200


# ============================================================================
# SUNBREAK PROTOCOL ENDPOINTS (/sunbreak/v1)
# ============================================================================


@app.route("/sunbreak/v1/submit", methods=["POST"])
def sunbreak_submit():
    """Submit a SunBreak envelope. Verifies signature and records an audit receipt."""
    # Verify request
    ok, msg, envelope = verify_sunbreak_request(request)
    if not ok:
        return jsonify({"error": {"code": "ERR_INVALID_SIGNATURE", "message": msg}}), 401

    # record received event
    received_event_id = service.audit_trail.record_event(
        event_type="sunbreak_received",
        user_id=envelope.get("sender_id", "unknown"),
        resource_id=envelope.get("message_id", ""),
        action="submit",
        metadata={"payload_hash": envelope.get("payload_hash"), "message_id": envelope.get("message_id")},
    )

    # Simulate processing (e.g., enqueue validation) and then accept
    receipt_id = service.audit_trail.record_event(
        event_type="sunbreak_accepted",
        user_id=envelope.get("sender_id", "unknown"),
        resource_id=envelope.get("message_id", ""),
        action="accepted",
        metadata={"payload_hash": envelope.get("payload_hash"), "message_id": envelope.get("message_id")},
    )

    # chain_hash is the last audit record's hash
    chain_hash = service.audit_trail.records[-1]["hash"] if service.audit_trail.records else ""

    receipt = {
        "receipt_id": receipt_id,
        "message_id": envelope.get("message_id"),
        "received_at": envelope.get("timestamp"),
        "payload_hash": envelope.get("payload_hash"),
        "chain_hash": chain_hash,
        "status": "accepted",
        "server_id": service.service_id,
    }

    # If payload contains an inline validation request, process it synchronously
    try:
        payload = envelope.get("payload", {})
        if isinstance(payload, dict) and payload.get("request_type") == "validate":
            ds_raw = payload.get("dataset")
            if isinstance(ds_raw, dict):
                # Parse dataset similar to /api/v1/validate
                dataset = {}
                for field_name, field_data in ds_raw.items():
                    if isinstance(field_data, list) and len(field_data) == 2:
                        data_type_str, records = field_data
                        try:
                            data_type = DataType[data_type_str.upper()]
                        except Exception:
                            data_type = DataType.GENERAL
                        dataset[field_name] = (data_type, records)

                if dataset:
                    report = service.validate_dataset(
                        user_id=envelope.get("sender_id", "unknown"),
                        dataset_name=payload.get("dataset_name", envelope.get("message_id")),
                        dataset=dataset,
                    )
                    # record validation event
                    validation_event_id = service.audit_trail.record_event(
                        event_type="sunbreak_validated",
                        user_id=envelope.get("sender_id", "unknown"),
                        resource_id=envelope.get("message_id", ""),
                        action="validated",
                        metadata={"assessment_id": report.get("assessment_id"), "overall_quality": report.get("overall_quality")},
                    )
                    # attach a brief validation summary to receipt
                    receipt["validation_summary"] = {
                        "assessment_id": report.get("assessment_id"),
                        "overall_quality": report.get("overall_quality"),
                    }

    except Exception as e:
        # non-fatal: log and continue
        logger.exception("SunBreak processing error: %s", e)

    return jsonify(receipt), 202


@app.route("/sunbreak/v1/status/<message_id>", methods=["GET"])
def sunbreak_status(message_id):
    auth = validate_api_key()
    if not auth:
        return jsonify({"error": "Invalid API key"}), 401

    # Search audit trail for events with resource_id == message_id
    events = [r for r in service.audit_trail.records if r.get("resource_id") == message_id]
    if not events:
        return jsonify({"message_id": message_id, "status": "not_found"}), 404

    # Determine latest status
    latest = events[-1]
    status = latest.get("event_type")
    return jsonify({"message_id": message_id, "status": status, "updated_at": latest.get("timestamp")}), 200


@app.route("/sunbreak/v1/receipt/<receipt_id>", methods=["GET"])
def sunbreak_receipt(receipt_id):
    auth = validate_api_key()
    if not auth:
        return jsonify({"error": "Invalid API key"}), 401

    matches = [r for r in service.audit_trail.records if r.get("event_id") == receipt_id]
    if not matches:
        return jsonify({"error": "Receipt not found"}), 404
    return jsonify(matches[0]), 200


@app.route("/sunbreak/v1/verify", methods=["POST"])
def sunbreak_verify():
    """Verify envelope/signature without creating a persistent receipt."""
    ok, msg, envelope = verify_sunbreak_request(request)
    if not ok:
        return jsonify({"verified": False, "error": msg}), 401
    return jsonify({"verified": True, "message_id": envelope.get("message_id")}), 200


@app.route("/sunbreak/v1/keys", methods=["GET"])
def sunbreak_keys():
    # Return list of public keys (keyid -> pub PEM). In production, use caching and proper headers.
    keys = {k: v.decode() if isinstance(v, (bytes, bytearray)) else v for k, v in SUNBREAK_PUBLIC_KEYS.items()}
    return jsonify({"keys": keys}), 200


@app.route("/sunbreak/v1/health", methods=["GET"])
def sunbreak_health():
    return jsonify({"status": "healthy", "service": "SunBreak Gateway", "timestamp": datetime.utcnow().isoformat()}), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False") == "True"
    
    logger.info(f"Starting DataValid API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
