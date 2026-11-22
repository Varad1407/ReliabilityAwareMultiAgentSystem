import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoring import score

SINGLE = {"expected_rows": [[534.40]]}
TOP = {
    "expected_rows": [["UK", 100.0], ["NL", 50.0], ["DE", 50.0]],
    "ordering": [{"column_index": 1, "direction": "desc"},
                 {"column_index": 0, "direction": "asc"}],
}


def test_exact_match():
    assert score([(534.40,)], SINGLE) == {"strict": True, "lenient": True, "matched_columns": [0]}


def test_unrounded_value_within_tolerance():
    assert score([(534.396,)], SINGLE)["strict"]


def test_wrong_value_rejected():
    assert not score([(540.0,)], SINGLE)["lenient"]


def test_extra_column_is_lenient_only():
    result = score([("avg", 534.40)], SINGLE)
    assert result["lenient"] and not result["strict"]


def test_wrong_order_rejected():
    rows = [("NL", 50.0), ("UK", 100.0), ("DE", 50.0)]
    assert not score(rows, TOP)["lenient"]


def test_tie_breaker_enforced():
    rows = [("UK", 100.0), ("DE", 50.0), ("NL", 50.0)]
    assert score(rows, TOP)["strict"]
    rows_bad = [("UK", 100.0), ("NL", 50.0), ("DE", 50.0)]
    assert not score(rows_bad, TOP)["lenient"]  # NL before DE breaks the alphabetical tie-break
