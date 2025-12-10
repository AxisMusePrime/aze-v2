"""Minimal Flask app showing a Stripe webhook handler.

Intended as an educational example only. Do not expose secret keys.
"""
from flask import Flask, request, jsonify
from datetime import datetime
import os
import stripe
import csv
from pathlib import Path

app = Flask(__name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
RECEIPTS_CSV = Path('financials/receipts/payment_receipts.csv')
LEDGER_CSV = Path('financials/receipts/ledger.csv')


def append_receipt(row: dict):
    """Append a receipt row to payment_receipts.csv and ledger.csv."""
    try:
        RECEIPTS_CSV.parent.mkdir(parents=True, exist_ok=True)
        # Append to receipts
        write_header = not RECEIPTS_CSV.exists() or RECEIPTS_CSV.stat().st_size == 0
        with open(RECEIPTS_CSV, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['invoice_number','received_at','payment_provider','provider_id','amount','currency','client','notes'])
            if write_header:
                writer.writeheader()
            writer.writerow(row)

        # Append to ledger (simple bookkeeping entry)
        ledger_write_header = not LEDGER_CSV.exists() or LEDGER_CSV.stat().st_size == 0
        with open(LEDGER_CSV, 'a', newline='') as f:
            ledger_writer = csv.DictWriter(f, fieldnames=['date','category','description','amount','currency','reference'])
            if ledger_write_header:
                ledger_writer.writeheader()
            ledger_writer.writerow({
                'date': row.get('received_at'),
                'category': 'payment',
                'description': f"Payment {row.get('provider_id')} for {row.get('invoice_number')}",
                'amount': row.get('amount'),
                'currency': row.get('currency','usd'),
                'reference': row.get('provider_id')
            })

    except Exception as e:
        print('Error writing receipt:', e)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create a Stripe Checkout session for a fixed item (demo)."""
    try:
        # Demo: charge $12.00 USD
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'VUA Monthly Hosting'},
                    'unit_amount': 1200,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.host_url + 'payments/success.html',
            cancel_url=request.host_url + 'payments/cancel.html',
        )

        return jsonify({'id': session.id, 'url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature', '')

    if WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        except ValueError:
            return jsonify({'error': 'Invalid payload'}), 400
        except stripe.error.SignatureVerificationError:
            return jsonify({'error': 'Invalid signature'}), 400
    else:
        # Development: parse body without verification
        try:
            event = stripe.Event.construct_from(request.get_json(), stripe.api_key)
        except Exception:
            return jsonify({'error': 'Invalid event'}), 400

    # Handle the event types you care about
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        # TODO: fulfill the order, mark invoice paid, etc.
        print('PaymentIntent succeeded:', intent.get('id'))
        # Record receipt (best-effort)
        try:
            row = {
                'invoice_number': intent.get('metadata', {}).get('invoice', ''),
                'received_at': intent.get('created') and datetime.utcfromtimestamp(intent.get('created')).isoformat() or datetime.utcnow().isoformat(),
                'payment_provider': 'stripe',
                'provider_id': intent.get('id'),
                'amount': float(intent.get('amount_received', intent.get('amount', 0))) / 100.0 if intent.get('amount') else 0.0,
                'currency': intent.get('currency', 'usd'),
                'client': intent.get('receipt_email') or intent.get('metadata', {}).get('client',''),
                'notes': intent.get('metadata', {}).get('notes','')
            }
            append_receipt(row)
        except Exception as e:
            print('Failed to record receipt:', e)
    elif event['type'] == 'invoice.payment_failed':
        print('Invoice payment failed')

    return jsonify({'received': True})


if __name__ == '__main__':
    app.run(port=5000)
