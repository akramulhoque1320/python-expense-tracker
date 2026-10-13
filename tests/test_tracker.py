import csv
import tempfile
import unittest
from pathlib import Path

from expense_tracker import ExpenseTracker
from expense_tracker.cli import main


class ExpenseTrackerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "expenses.json"
        self.tracker = ExpenseTracker(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_assigns_ids_and_persists(self):
        self.tracker.add(120, "Food", "Lunch", "2026-10-01")
        self.tracker.add(50.5, "transport", on="2026-10-02")
        reloaded = ExpenseTracker(self.path)
        self.assertEqual([e.id for e in reloaded.expenses], [1, 2])
        self.assertEqual(reloaded.expenses[0].category, "food")

    def test_add_rejects_non_positive_amount(self):
        with self.assertRaises(ValueError):
            self.tracker.add(0, "food")

    def test_add_rejects_bad_date(self):
        with self.assertRaises(ValueError):
            self.tracker.add(10, "food", on="13-10-2026")

    def test_filter_by_category_and_month(self):
        self.tracker.add(100, "food", on="2026-09-30")
        self.tracker.add(200, "food", on="2026-10-05")
        self.tracker.add(300, "rent", on="2026-10-01")
        self.assertEqual(len(self.tracker.filter(category="food")), 2)
        self.assertEqual([e.amount for e in self.tracker.filter(month="2026-10")], [300, 200])

    def test_summary_sorted_by_total(self):
        self.tracker.add(100, "food", on="2026-10-01")
        self.tracker.add(150, "food", on="2026-10-02")
        self.tracker.add(500, "rent", on="2026-10-01")
        self.assertEqual(self.tracker.summary(), {"rent": 500, "food": 250})
        self.assertEqual(self.tracker.total(), 750)

    def test_delete(self):
        e = self.tracker.add(10, "misc")
        self.assertTrue(self.tracker.delete(e.id))
        self.assertFalse(self.tracker.delete(e.id))
        self.assertEqual(ExpenseTracker(self.path).expenses, [])

    def test_export_csv(self):
        self.tracker.add(10, "misc", "pen", "2026-10-01")
        out = Path(self.tmp.name) / "out.csv"
        self.assertEqual(self.tracker.export_csv(out), 1)
        with open(out, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["description"], "pen")

    def test_cli_add_and_delete(self):
        self.assertEqual(main(["--file", str(self.path), "add", "25", "coffee"]), 0)
        self.assertEqual(main(["--file", str(self.path), "delete", "1"]), 0)
        self.assertEqual(main(["--file", str(self.path), "delete", "1"]), 1)


if __name__ == "__main__":
    unittest.main()
