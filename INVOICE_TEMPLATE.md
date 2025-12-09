# Invoice Template — VUA TOTALITY

Company: ____________________
Address: ____________________
Email: ______________________

Invoice #: INVOICE-0001
Date: YYYY-MM-DD
Due Date: YYYY-MM-DD

Bill To:
Client Name: __________________
Client Address: ________________
Client Email: __________________

---

Description | Qty | Unit Price (USD) | Line Total (USD)
---|---:|---:|---:
Project setup & deployment | 1 | $XXXX.00 | $XXXX.00
Manifest creation & attestation | 1 | $XXX.00 | $XXX.00
1 month hosting & maintenance (minimal) | 1 | $XX.00 | $XX.00
Support & SLA (optional, monthly) | 1 | $XXX.00 | $XXX.00

Subtotal: $XXXX.00
Sales Tax (if applicable): $XX.XX
Total Due: $XXXX.00

Payment Instructions
- Bank Transfer (wire): Account Name: __________, Bank: __________, IBAN/SWIFT: __________
- PayPal: paypal.me/yourname (or business account email)
- Stripe (card): See payment integration steps in `PAYMENT_INTEGRATION.md`

Notes
- Please include the invoice number on payment.
- Late payments incur X% per month (optional).

CSV invoice example (columns: description,qty,unit_price,line_total)
"Project setup & deployment",1,1000.00,1000.00
"Monthly hosting",1,12.00,12.00
"Support SLA (monthly)",1,300.00,300.00

---

Thank you for your business.
