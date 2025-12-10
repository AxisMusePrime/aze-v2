#!/usr/bin/env python3
"""Generate a printable PDF invoice using ReportLab.

Requires: reportlab

Usage:
  python financials/generate_invoice_pdf.py INVOICE-0001
"""
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


def generate(invoice_number, client='Client Name', items=None, out='invoice.pdf'):
    items = items or [
        ('Project setup & deployment', 1, 1500.00),
        ('Monthly hosting', 1, 12.00),
    ]

    c = canvas.Canvas(out, pagesize=A4)
    width, height = A4

    c.setFont('Helvetica-Bold', 16)
    c.drawString(40, height - 60, 'Invoice')
    c.setFont('Helvetica', 10)
    c.drawString(40, height - 80, f'Invoice #: {invoice_number}')
    c.drawString(40, height - 95, f'Date: {datetime.utcnow().date()}')

    y = height - 140
    c.setFont('Helvetica-Bold', 11)
    c.drawString(40, y, 'Description')
    c.drawString(360, y, 'Qty')
    c.drawString(420, y, 'Unit')
    c.drawString(500, y, 'Total')
    c.setFont('Helvetica', 10)
    y -= 20

    total = 0.0
    for desc, qty, unit in items:
        line_total = qty * unit
        c.drawString(40, y, desc)
        c.drawString(360, y, str(qty))
        c.drawString(420, y, f'${unit:.2f}')
        c.drawString(500, y, f'${line_total:.2f}')
        y -= 18
        total += line_total

    y -= 10
    c.setFont('Helvetica-Bold', 11)
    c.drawString(420, y, 'Total:')
    c.drawString(500, y, f'${total:.2f}')

    c.showPage()
    c.save()
    print(f'Invoice written to {out}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: generate_invoice_pdf.py INVOICE-NUMBER')
        sys.exit(1)
    generate(sys.argv[1], out=f'{sys.argv[1]}.pdf')
