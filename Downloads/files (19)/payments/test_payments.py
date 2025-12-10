import json
import os
import tempfile
from payments import app


def test_webhook_records_receipt(tmp_path, monkeypatch):
    # Use test client
    client = app.test_client()

    # Prepare a fake payment_intent.succeeded event payload
    event = {
        'type': 'payment_intent.succeeded',
        'data': {
            'object': {
                'id': 'pi_test_123',
                'amount': 1200,
                'amount_received': 1200,
                'currency': 'usd',
                'created': 1700000000,
                'metadata': {'invoice': 'INVOICE-TEST', 'client': 'TestClient'},
                'receipt_email': 'buyer@example.com'
            }
        }
    }

    # Ensure receipts path uses tmpdir
    receipts_dir = tmp_path / 'financials' / 'receipts'
    receipts_dir.mkdir(parents=True)
    monkeypatch.setenv('STRIPE_WEBHOOK_SECRET', '')
    # Patch Path locations in module
    from pathlib import Path
    payments_module = __import__('payments.app', fromlist=['RECEIPTS_CSV'])
    payments_module.RECEIPTS_CSV = Path(receipts_dir / 'payment_receipts.csv')
    payments_module.LEDGER_CSV = Path(receipts_dir / 'ledger.csv')

    resp = client.post('/webhook', json=event)
    assert resp.status_code == 200

    # Check that receipt file exists and contains invoice
    with open(payments_module.RECEIPTS_CSV, 'r') as f:
        content = f.read()
    assert 'INVOICE-TEST' in content
