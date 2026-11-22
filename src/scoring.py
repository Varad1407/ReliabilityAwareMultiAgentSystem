"""
Shared scoring for Systems A, B and C.

Every system is scored by the same function so that comparisons are fair.

Two verdicts are produced for each answer:
- strict:  the result has exactly the expected columns, in order.
- lenient: the expected columns can be found inside the result, in order,
           even if the system returned extra columns (e.g. a label column).

Numbers are compared with a small tolerance (ABS_TOL) so that answers that
differ only by rounding to 2 decimal places are not marked wrong.
"""

import math
from itertools import combinations

ABS_TOL = 0.01
REL_TOL = 1e-6
MAX_COLUMNS_FOR_PROJECTION = 8


def values_match(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL)
    return a == b


def rows_equal(actual_row, expected_row):
    return len(actual_row) == len(expected_row) and all(
        values_match(a, e) for a, e in zip(actual_row, expected_row)
    )


def rows_match_unordered(actual_rows, expected_rows):
    if len(actual_rows) != len(expected_rows):
        return False
    unmatched = list(expected_rows)
    for row in actual_rows:
        for i, expected in enumerate(unmatched):
            if rows_equal(row, expected):
                unmatched.pop(i)
                break
        else:
            return False
    return True


def ordering_ok(rows, ordering):
    """Check ordering rules (column_index refers to the expected columns)."""
    if not ordering or len(rows) < 2:
        return True
    for current, nxt in zip(rows, rows[1:]):
        for rule in ordering:
            i = rule["column_index"]
            a, b = current[i], nxt[i]
            if values_match(a, b):
                continue
            if rule["direction"].lower() == "asc" and a > b:
                return False
            if rule["direction"].lower() == "desc" and a < b:
                return False
            break
    return True


def _check(rows, item):
    expected = item["expected_rows"]
    return rows_match_unordered(rows, expected) and ordering_ok(rows, item.get("ordering"))


def score(actual_rows, item):
    """
    Return {"strict": bool, "lenient": bool, "matched_columns": list|None}.
    actual_rows: list of rows (tuples or lists) returned by the system.
    """
    rows = [list(r) for r in (actual_rows or [])]
    expected = item["expected_rows"]
    width = len(expected[0]) if expected else 0

    if rows and len(rows[0]) == width and _check(rows, item):
        return {"strict": True, "lenient": True, "matched_columns": list(range(width))}

    if not rows or not expected:
        return {"strict": False, "lenient": False, "matched_columns": None}

    actual_width = len(rows[0])
    if width < actual_width <= MAX_COLUMNS_FOR_PROJECTION:
        for cols in combinations(range(actual_width), width):
            projected = [[r[c] for c in cols] for r in rows]
            if _check(projected, item):
                return {"strict": False, "lenient": True, "matched_columns": list(cols)}

    return {"strict": False, "lenient": False, "matched_columns": None}
