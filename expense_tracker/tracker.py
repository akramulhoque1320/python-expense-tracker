"""Core logic for storing and summarising expenses."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path


@dataclass
class Expense:
    id: int
    amount: float
    category: str
    description: str
    date: str  # ISO format, e.g. "2026-10-13"


class ExpenseTracker:
    """Keeps a list of expenses in a JSON file."""

    def __init__(self, path: str | Path = "expenses.json"):
        self.path = Path(path)
        self.expenses: list[Expense] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8") or "[]")
            self.expenses = [Expense(**item) for item in data]

    def _save(self) -> None:
        self.path.write_text(
            json.dumps([asdict(e) for e in self.expenses], indent=2),
            encoding="utf-8",
        )

    def add(self, amount: float, category: str, description: str = "", on: str | None = None) -> Expense:
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        expense_date = date.fromisoformat(on) if on else date.today()
        next_id = max((e.id for e in self.expenses), default=0) + 1
        expense = Expense(
            id=next_id,
            amount=round(amount, 2),
            category=category.strip().lower(),
            description=description.strip(),
            date=expense_date.isoformat(),
        )
        self.expenses.append(expense)
        self._save()
        return expense

    def delete(self, expense_id: int) -> bool:
        before = len(self.expenses)
        self.expenses = [e for e in self.expenses if e.id != expense_id]
        if len(self.expenses) == before:
            return False
        self._save()
        return True

    def filter(self, category: str | None = None, month: str | None = None) -> list[Expense]:
        """Return expenses, optionally for one category and/or month ("YYYY-MM")."""
        result = self.expenses
        if category:
            result = [e for e in result if e.category == category.strip().lower()]
        if month:
            result = [e for e in result if e.date.startswith(month)]
        return sorted(result, key=lambda e: (e.date, e.id))

    def summary(self, month: str | None = None) -> dict[str, float]:
        """Total spent per category, largest first."""
        totals: dict[str, float] = {}
        for e in self.filter(month=month):
            totals[e.category] = round(totals.get(e.category, 0) + e.amount, 2)
        return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))

    def total(self, month: str | None = None) -> float:
        return round(sum(e.amount for e in self.filter(month=month)), 2)

    def export_csv(self, out_path: str | Path) -> int:
        rows = self.filter()
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "date", "category", "amount", "description"])
            writer.writeheader()
            for e in rows:
                writer.writerow({k: getattr(e, k) for k in writer.fieldnames})
        return len(rows)
