# Python Expense Tracker

A command-line expense tracker written in pure **Python 3.10+** with no external dependencies. Expenses are stored in a JSON file.

## Features

- Add expenses with amount, category, description and date
- List and filter by category or month
- Monthly summary per category with percentage bars
- Delete by id
- Export to CSV
- Unit tests with `unittest`

## Usage

```bash
python -m expense_tracker add 250 food -d "Lunch with team"
python -m expense_tracker add 1200 rent --date 2026-10-01
python -m expense_tracker list --month 2026-10
python -m expense_tracker summary
python -m expense_tracker delete 2
python -m expense_tracker export expenses.csv
```

Example summary:

```
rent              1200.00   82.8%  #################
food               250.00   17.2%  ###
TOTAL             1450.00
```

Use `--file other.json` before the command to use a different data file.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```
expense_tracker/
  tracker.py    # Expense data class and ExpenseTracker logic
  cli.py        # argparse command-line interface
  __main__.py   # entry point for `python -m expense_tracker`
tests/
  test_tracker.py
```
