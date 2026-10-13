"""Command-line interface: python -m expense_tracker <command> ..."""

from __future__ import annotations

import argparse
import sys

from .tracker import ExpenseTracker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="expense_tracker", description="Track your daily expenses.")
    parser.add_argument("--file", default="expenses.json", help="data file (default: expenses.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add an expense")
    add.add_argument("amount", type=float)
    add.add_argument("category")
    add.add_argument("-d", "--description", default="")
    add.add_argument("--date", help="YYYY-MM-DD (default: today)")

    ls = sub.add_parser("list", help="list expenses")
    ls.add_argument("-c", "--category")
    ls.add_argument("-m", "--month", help="YYYY-MM")

    summary = sub.add_parser("summary", help="totals per category")
    summary.add_argument("-m", "--month", help="YYYY-MM")

    delete = sub.add_parser("delete", help="delete an expense by id")
    delete.add_argument("id", type=int)

    export = sub.add_parser("export", help="export all expenses to CSV")
    export.add_argument("output", help="output .csv path")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tracker = ExpenseTracker(args.file)

    try:
        if args.command == "add":
            e = tracker.add(args.amount, args.category, args.description, args.date)
            print(f"Added #{e.id}: {e.amount:.2f} for {e.category} on {e.date}")

        elif args.command == "list":
            rows = tracker.filter(args.category, args.month)
            if not rows:
                print("No expenses found.")
            else:
                print(f"{'ID':>4}  {'Date':<10}  {'Category':<14}  {'Amount':>10}  Description")
                print("-" * 60)
                for e in rows:
                    print(f"{e.id:>4}  {e.date:<10}  {e.category:<14}  {e.amount:>10.2f}  {e.description}")
                print("-" * 60)
                print(f"{'Total':<32}  {sum(e.amount for e in rows):>10.2f}")

        elif args.command == "summary":
            totals = tracker.summary(args.month)
            if not totals:
                print("No expenses found.")
            else:
                grand = tracker.total(args.month)
                for category, amount in totals.items():
                    share = amount / grand * 100
                    bar = "#" * round(share / 5)
                    print(f"{category:<14} {amount:>10.2f}  {share:5.1f}%  {bar}")
                print(f"{'TOTAL':<14} {grand:>10.2f}")

        elif args.command == "delete":
            if tracker.delete(args.id):
                print(f"Deleted #{args.id}")
            else:
                print(f"No expense with id {args.id}", file=sys.stderr)
                return 1

        elif args.command == "export":
            count = tracker.export_csv(args.output)
            print(f"Exported {count} expenses to {args.output}")

    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0
