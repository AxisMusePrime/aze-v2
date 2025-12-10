#!/usr/bin/env python3
"""Compute simple monthly P&L and amortization schedule from sample CSVs.

Usage:
  python financials/compute_financials.py --months 12
"""
import csv
import argparse
from datetime import datetime
from decimal import Decimal


def read_csv(path):
    rows = []
    try:
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except FileNotFoundError:
        return []
    return rows


def to_decimal(x):
    try:
        return Decimal(x)
    except Exception:
        return Decimal('0')


def sum_amounts(rows):
    return sum(to_decimal(r.get('amount', '0')) for r in rows)


def compute_amortization(capitalized_cost, months):
    monthly = Decimal(capitalized_cost) / Decimal(months)
    schedule = []
    remaining = Decimal(capitalized_cost)
    for m in range(1, months + 1):
        remaining -= monthly
        schedule.append({'month': m, 'amortization': float(round(monthly, 2)), 'remaining': float(round(max(remaining, 0), 2))})
    return schedule


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--months', type=int, default=12, help='Months for projection and amortization')
    args = parser.parse_args()

    income = read_csv('financials/income.csv')
    expenses = read_csv('financials/expenses.csv')
    invoices = read_csv('financials/invoices.csv')

    total_income = sum_amounts(income)
    total_expenses = sum_amounts(expenses)

    # Example: treat development and setup (first expense rows) as capitalized
    capitalized = 0
    for r in expenses:
        if 'setup' in r.get('description','').lower() or 'development' in r.get('category','').lower() or 'professional' in r.get('category','').lower():
            capitalized += float(r.get('amount') or 0)

    amort_months = max(args.months, 1)
    amort_schedule = compute_amortization(capitalized, amort_months)
    monthly_amort = amort_schedule[0]['amortization'] if amort_schedule else 0

    # Monthly totals (simple equal division for demo)
    monthly_income = float(total_income) / amort_months
    monthly_operating = float(total_expenses) / amort_months

    print('\nFinancial Summary ({} months projection)'.format(amort_months))
    print('----------------------------------------')
    print('Total income: ${:.2f}'.format(float(total_income)))
    print('Total expenses: ${:.2f}'.format(float(total_expenses)))
    print('Capitalized cost (for amortization): ${:.2f}'.format(float(capitalized)))
    print('\nMonthly Estimates (simple projection)')
    print('  Avg monthly income: ${:.2f}'.format(monthly_income))
    print('  Avg monthly operating expense: ${:.2f}'.format(monthly_operating))
    print('  Monthly amortization: ${:.2f}'.format(monthly_amort))
    print('  Estimated monthly profit: ${:.2f}'.format(monthly_income - monthly_operating - monthly_amort))

    print('\nAmortization schedule (first 12 months shown)')
    for e in amort_schedule[:12]:
        print('  Month {month}: amortization ${amortization:.2f}, remaining ${remaining:.2f}'.format(**e))

    print('\nOpen invoices:')
    for inv in invoices:
        print('  {invoice_number} | {date} | {client} | ${amount} | {status}'.format(**inv))


if __name__ == '__main__':
    main()
