# Payments example (Flask + Stripe)

This folder contains a minimal Flask app demonstrating how to accept payments (Stripe) and process webhooks.

Files:
- `app.py` — Minimal Flask app with a `/webhook` endpoint to handle Stripe events and a placeholder `/health`.
- `requirements.txt` — Python packages required: `flask`, `stripe`.

Notes:
- Do NOT commit real Stripe secret keys. Use environment variables: `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`.
- For production, use HTTPS and verify webhook signatures.
- This is a minimal reference; for production use Stripe's official examples and SDK docs.

Run locally (development):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r payments/requirements.txt
export STRIPE_SECRET_KEY=sk_test_xxx
export STRIPE_WEBHOOK_SECRET=whsec_xxx
flask --app payments.app run --port 5000
```
