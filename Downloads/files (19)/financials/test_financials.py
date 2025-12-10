from financials import compute_financials


def test_compute_financials_runs(monkeypatch, tmp_path):
    # Create sample CSVs in tmp path
    income = tmp_path / 'income.csv'
    income.write_text('description,date,amount,notes\n"Support",2025-12-01,300.00,""\n')
    expenses = tmp_path / 'expenses.csv'
    expenses.write_text('description,date,amount,category,notes\n"Setup",2025-12-01,1500.00,Professional,""\n')

    monkeypatch.chdir(tmp_path)
    # Should run without error
    compute_financials.main()
