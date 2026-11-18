
import math


def values_match(a, b):
    """Compare values while allowing small floating-point differences."""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-6)

    return a == b


def rows_match(actual_rows, expected_rows):
    """Compare rows without requiring a particular row order."""
    if len(actual_rows) != len(expected_rows):
        return False

    unmatched = list(expected_rows)

    for actual_row in actual_rows:
        for index, expected_row in enumerate(unmatched):
            if (
                len(actual_row) == len(expected_row)
                and all(
                    values_match(a, b)
                    for a, b in zip(actual_row, expected_row)
                )
            ):
                unmatched.pop(index)
                break
        else:
            return False

    return len(unmatched) == 0


def ordering_matches(rows, ordering):
    """Check one or more ordering rules, including tie-breakers."""
    if not ordering or len(rows) < 2:
        return True

    for current_row, next_row in zip(rows, rows[1:]):
        for rule in ordering:
            column_index = rule["column_index"]
            direction = rule["direction"].lower()

            current_value = current_row[column_index]
            next_value = next_row[column_index]

            if values_match(current_value, next_value):
                continue

            if direction == "asc":
                if current_value > next_value:
                    return False
            elif direction == "desc":
                if current_value < next_value:
                    return False
            else:
                raise ValueError(
                    f"Unsupported ordering direction: {direction}"
                )

            break

    return True
