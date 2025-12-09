# Payment Integration Instructions — VUA TOTALITY

This document outlines simple steps to accept payments using Stripe and PayPal. These instructions are intentionally minimal and are intended for a developer familiar with webhooks and secure key handling.

Stripe (recommended for card payments)
1) Create a Stripe account at https://dashboard.stripe.com/register.
2) In the Dashboard, get your API keys: Publishable key and Secret key (use test keys while developing).
3) Server-side: Install Stripe SDK or use direct HTTP calls. For Python, `stripe` SDK is available (pip). If you must use stdlib-only, call Stripe HTTP API with `requests` (or built-in `urllib`) — note this requires TLS and more manual handling.

Basic flow (server-side)
- Create a PaymentIntent via Stripe API with amount, currency, and metadata (invoice number).
- Return client secret to frontend.
- Accept payment on the frontend using Stripe.js (card element) or redirect to Checkout.
- Implement webhook endpoint to listen for `payment_intent.succeeded` and update your ledger/invoices.

Security
- Never commit secret keys to source control. Use environment variables.
- Use HTTPS for webhook endpoints. Validate webhook signatures using the signing secret from Stripe.

PayPal (alternative)
1) Create a Business account on PayPal.
2) Use the REST API credentials (Client ID and Secret).
3) Use PayPal Checkout or subscription APIs for recurring billing.
4) Implement IPN or Webhooks to verify payments and update invoices.

Accepting recurring payments
- Stripe Subscriptions: Create Products and Plans in Stripe. Use Checkout or the Subscriptions API to manage recurring billing.
- PayPal Subscriptions: Use Billing Plans and Agreements.

Offline payments
- Provide bank transfer or PayPal.Me links on invoices.
- Mark invoice as paid upon receipt and record transaction id.

Minimal implementation recommendation (fastest)
- Use Stripe Checkout for one-off payments or subscriptions (few lines to integrate).
- Use webhooks for reliable payment confirmation.

Example: create a PaymentIntent (curl)
```bash
curl https://api.stripe.com/v1/payment_intents \
  -u sk_test_YOUR_SECRET_KEY: \
  -d amount=1000 \
  -d currency=usd \
  -d "payment_method_types[]"=card
```

Notes
- If you require an example implementation in pure Python for webhook handling and ledger updates, I can add a `payments/` folder with a minimal Flask or FastAPI example. Stripe officially provides SDKs for convenience but are optional.

Compliance & Taxes
- Collect tax information based on jurisdiction.
- Issue invoices and keep records for tax purposes.
- Consult an accountant for VAT/GST specifics.
