# Billing Workflow — VUA TOTALITY

This document describes a simple reusable billing workflow from proposal to payment and record-keeping.

1. Proposal & Scope
   - Agree scope, deliverables, and timelines with client.
   - Provide a written quote including one-time and recurring costs.

2. Contract & Invoice Terms
   - Specify payment terms (50% upfront for services, remainder on delivery; monthly for subscriptions).
   - Specify late fees and refund policy.

3. Create Invoice
   - Use `INVOICE_TEMPLATE.md` to create an invoice. Assign invoice number and due date.

4. Send Invoice & Track
   - Email invoice with payment instructions. Track in `financials/invoices.csv`.

5. Receive Payment
   - For card payments, reconcile via Stripe dashboard/webhook.
   - For wire/ACH, record transaction id and mark invoice paid.

6. Record & Archive
   - Store invoice PDF and payment receipt in `financials/receipts/` (create if needed).
   - Update bookkeeping CSVs (income/expenses) and run `financials/compute_financials.py` monthly.

7. Renewals & Subscriptions
   - Use Stripe subscriptions for recurring billing; monitor failed payments and notify client.

Notes
- Automate where possible: webhooks → mark invoice paid → send receipt.
- Keep backup copies and maintain separate bank account for project funds.
