import sqlite3
import random
from pathlib import Path


# Find the main project directory
project_dir = Path(__file__).resolve().parent.parent

# Define the database location
database_path = project_dir / "data" / "novaretail.db"

# Create a reproducible random generator
rng = random.Random(42)


# Customer sample data
customer_names = [
    "Aarav Sharma", "Priya Patel", "Rohan Mehta", "Ananya Singh",
    "Ishaan Gupta", "Sneha Rao", "Kabir Shah", "Diya Joshi",
    "Arjun Nair", "Meera Iyer", "Vivaan Desai", "Aisha Khan",
    "Reyansh Kulkarni", "Saanvi Reddy", "Aditya Verma",
    "Kavya Menon", "Rahul Das", "Ira Kapoor", "Dev Malhotra",
    "Tara Bose", "Neil Thomas", "Riya Chavan", "Omkar Pawar",
    "Simran Kaur", "Karan Sethi", "Nisha Jain", "Siddharth Roy",
    "Pooja Mishra", "Yash Bhat", "Maya Fernandes"
]

cities = [
    "Pune", "Mumbai", "Delhi", "Bengaluru", "Hyderabad",
    "Chennai", "Kolkata", "Jaipur", "Ahmedabad", "Nagpur"
]

# Product sample data
product_catalogue = [
    ("Laptop", "Electronics", 65000, 15),
    ("Smartphone", "Electronics", 35000, 25),
    ("Headphones", "Electronics", 2500, 50),
    ("Keyboard", "Electronics", 1800, 40),
    ("Mouse", "Electronics", 900, 60),
    ("Office Chair", "Furniture", 8500, 12),
    ("Study Desk", "Furniture", 12000, 10),
    ("Bookshelf", "Furniture", 6000, 8),
    ("Running Shoes", "Fashion", 3200, 30),
    ("T-Shirt", "Fashion", 800, 70),
    ("Jeans", "Fashion", 2200, 35),
    ("Jacket", "Fashion", 4500, 20),
    ("Coffee Maker", "Appliances", 4200, 18),
    ("Mixer Grinder", "Appliances", 5500, 14),
    ("Microwave", "Appliances", 9500, 9),
    ("Water Bottle", "Accessories", 500, 100),
    ("Backpack", "Accessories", 1600, 45),
    ("Wrist Watch", "Accessories", 2800, 25),
    ("Notebook", "Stationery", 120, 200),
    ("Pen Set", "Stationery", 250, 150)
]


# Possible order statuses
order_statuses = [
    "Pending",
    "Processing",
    "Shipped",
    "Delivered",
    "Cancelled"
]


# Date range for customer signups and orders
from datetime import date, timedelta

start_date = date(2025, 1, 1)
end_date = date(2025, 12, 31)

def generate_customers():
    customers = []

    total_days = (end_date - start_date).days

    for customer_id, name in enumerate(customer_names, start=1):

        city = rng.choice(cities)

        signup_date = start_date + timedelta(
            days=rng.randint(0, total_days)
        )

        customers.append((
            customer_id,
            name,
            city,
            signup_date.isoformat()
        ))

    return customers

def generate_products():
    products = []

    for product_id, product in enumerate(product_catalogue, start=1):

        product_name, category, price_rupees, stock_quantity = product

        price_paise = price_rupees * 100

        products.append((
            product_id,
            product_name,
            category,
            price_paise,
            stock_quantity
        ))

    return products

def generate_orders(customers, total_orders=100):

    orders = []

    # Store each customer's signup date
    customer_signup_dates = {
        customer[0]: date.fromisoformat(customer[3])
        for customer in customers
    }

    for order_id in range(1, total_orders + 1):

        # Select a customer
        customer_id = rng.randint(1, len(customers))

        # Get this customer's signup date
        signup_date = customer_signup_dates[customer_id]

        # Generate an order date on or after signup
        available_days = (end_date - signup_date).days

        order_date = signup_date + timedelta(
            days=rng.randint(0, available_days)
        )

        status = rng.choice(order_statuses)

        orders.append((
            order_id,
            customer_id,
            order_date.isoformat(),
            status
        ))

    return orders

def generate_order_items(total_orders=100):
    order_items = []
    order_item_id = 1

    for order_id in range(1, total_orders + 1):

        # Each order contains between 1 and 4 products
        number_of_items = rng.randint(1, 4)

        # Select products without duplicates within the same order
        selected_products = rng.sample(
            range(1, len(product_catalogue) + 1),
            number_of_items
        )

        for product_id in selected_products:

            quantity = rng.randint(1, 5)

            # Get the original product price
            price_rupees = product_catalogue[product_id - 1][2]

            # Apply a small historical price variation
            price_variation = rng.choice([0.90, 0.95, 1.00, 1.05])

            unit_price_paise = int(
                price_rupees * price_variation * 100
            )

            order_items.append((
                order_item_id,
                order_id,
                product_id,
                quantity,
                unit_price_paise
            ))

            order_item_id += 1

    return order_items

def seed_database():

    customers = generate_customers()
    products = generate_products()
    orders = generate_orders(customers)
    order_items = generate_order_items()

    with sqlite3.connect(database_path) as connection:

        connection.execute("PRAGMA foreign_keys = ON;")

        # Clear existing records before inserting fresh data
        connection.execute("DELETE FROM order_items;")
        connection.execute("DELETE FROM orders;")
        connection.execute("DELETE FROM products;")
        connection.execute("DELETE FROM customers;")

        # Insert customers
        connection.executemany("""
            INSERT INTO customers
            (customer_id, customer_name, city, signup_date)
            VALUES (?, ?, ?, ?)
        """, customers)

        # Insert products
        connection.executemany("""
            INSERT INTO products
            (product_id, product_name, category,
             current_price_paise, stock_quantity)
            VALUES (?, ?, ?, ?, ?)
        """, products)

        # Insert orders
        connection.executemany("""
            INSERT INTO orders
            (order_id, customer_id, order_date, status)
            VALUES (?, ?, ?, ?)
        """, orders)

        # Insert order items
        connection.executemany("""
            INSERT INTO order_items
            (order_item_id, order_id, product_id,
             quantity, unit_price_paise)
            VALUES (?, ?, ?, ?, ?)
        """, order_items)

        # Verify the number of records in each table
        print("\nDatabase record counts:")

        for table_name in [
            "customers",
            "products",
            "orders",
            "order_items"
        ]:
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name};"
            ).fetchone()[0]

            print(f"{table_name}: {count}")

    print("NovaRetail database seeded successfully!")

if __name__ == "__main__":
    seed_database()
