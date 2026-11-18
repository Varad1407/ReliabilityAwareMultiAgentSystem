
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from evaluation_utils import (
    rows_match,
    ordering_matches,
    values_match
)


class TestEvaluationFunctions(unittest.TestCase):

    def test_correct_rows_match(self):
        actual = [
            ("Alice", 10),
            ("Bob", 5)
        ]

        expected = [
            ("Bob", 5),
            ("Alice", 10)
        ]

        self.assertTrue(rows_match(actual, expected))

    def test_incorrect_rows_do_not_match(self):
        actual = [
            ("Alice", 10),
            ("Bob", 7)
        ]

        expected = [
            ("Alice", 10),
            ("Bob", 5)
        ]

        self.assertFalse(rows_match(actual, expected))

    def test_descending_order_is_valid(self):
        rows = [
            ("Laptop", 50),
            ("Phone", 30),
            ("Headphones", 10)
        ]

        ordering = [
            {"column_index": 1, "direction": "desc"}
        ]

        self.assertTrue(ordering_matches(rows, ordering))

    def test_incorrect_descending_order_is_rejected(self):
        rows = [
            ("Laptop", 10),
            ("Phone", 30),
            ("Headphones", 20)
        ]

        ordering = [
            {"column_index": 1, "direction": "desc"}
        ]

        self.assertFalse(ordering_matches(rows, ordering))

    def test_alphabetical_tie_breaking(self):
        rows = [
            ("Alice", 10),
            ("Bob", 10),
            ("Charlie", 5)
        ]

        ordering = [
            {"column_index": 1, "direction": "desc"},
            {"column_index": 0, "direction": "asc"}
        ]

        self.assertTrue(ordering_matches(rows, ordering))

    def test_incorrect_alphabetical_tie_breaking(self):
        rows = [
            ("Bob", 10),
            ("Alice", 10),
            ("Charlie", 5)
        ]

        ordering = [
            {"column_index": 1, "direction": "desc"},
            {"column_index": 0, "direction": "asc"}
        ]

        self.assertFalse(ordering_matches(rows, ordering))

    def test_equal_values_are_valid_without_tie_break_rule(self):
        rows = [
            ("Laptop", 50),
            ("Phone", 50),
            ("Headphones", 10)
        ]

        ordering = [
            {"column_index": 1, "direction": "desc"}
        ]

        self.assertTrue(ordering_matches(rows, ordering))

    def test_floating_point_comparison(self):
        self.assertTrue(values_match(10.0000001, 10.0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
