# Accounting Summary — VUA TOTALITY (Sample)

This file outlines a simple accounting summary for the project: expenses, amortization, revenue scenarios, and profit estimates.

Assumptions (example)
- Initial development cost (labor + setup): $4,000 (one-time)
- One-time setup & legal: $800
- Monthly operating expenses (minimal): $12/month
- Monthly recurring revenue (example): $300/month (support+hosting for 1 client)

Initial Capital & Costs
- Development & setup: $4,800 (capitalized)
- Cash on hand for 6 months: $500

Amortization (straight-line)
- Capitalized cost: $4,800
- Useful life: 36 months
- Monthly amortization: $4,800 / 36 = $133.33/month

Monthly Income Statement (example, month 1)
- Revenue: $300
- Operating expense: $12
- Amortization: $133.33
- Gross Profit: 300 - 12 - 133.33 = $154.67

Break-even analysis
- Monthly break-even revenue = Operating expense + Amortization
- = 12 + 133.33 = $145.33
- So a single $300/month client covers costs and yields profit.

Year 1 projection (conservative)
- Average monthly clients: 3
- Monthly revenue: 3 * $300 = $900
- Annual revenue: $10,800
- Annual operating expenses: 12 * $12 = $144
- Annual amortization: 12 * 133.33 = $1,599.96
- Estimated annual profit: 10,800 - 144 - 1,599.96 = $9,056.04

Accounting Notes
- Keep separate bank account and bookkeeping records.
- Record one-time capital expenses as assets and amortize.
- Record monthly hosting/support revenue as recurring revenue.
- Track tax liabilities and consult an accountant for local tax rules.

Templates & Files
- Use `INVOICE_TEMPLATE.md` for billing.
- Keep a `financials/` directory with CSV exports: income.csv, expenses.csv, invoices.csv.

Next steps
- If you want, I can create a small `financials/` folder in the repo with sample CSVs and a simple Python script to calculate amortization and P&L.
