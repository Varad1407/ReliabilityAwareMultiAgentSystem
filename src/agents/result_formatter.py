
def format_query_results(columns, rows):
    """
    Formats database rows without changing their
    original order or removing any records.
    """

    formatted_results = []

    for index, row in enumerate(rows, start=1):

        if len(columns) == 1:
            formatted_line = f"{index}. {row[0]}"

        else:
            values = []

            for column, value in zip(columns, row):
                values.append(f"{column}: {value}")

            formatted_line = (
                f"{index}. " + " | ".join(values)
            )

        formatted_results.append(formatted_line)

    return "\n".join(formatted_results)


if __name__ == "__main__":

    columns = ["customer_name", "order_count"]

    rows = [
        ("Rohan Mehta", 6),
        ("Aditya Verma", 5),
        ("Arjun Nair", 4),
        ("Karan Sethi", 4),
        ("Maya Fernandes", 4)
    ]

    result = format_query_results(columns, rows)

    print("\nFORMATTED DATABASE RESULTS")
    print("=" * 40)
    print(result)
