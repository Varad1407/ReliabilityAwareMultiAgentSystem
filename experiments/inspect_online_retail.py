
import pandas as pd

file_path = "../data/Online Retail.xlsx"

df = pd.read_excel(file_path)

print("\n--- DATASET OVERVIEW ---")
print("Number of rows and columns:", df.shape)

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- FIRST 5 ROWS ---")
print(df.head())

print("\n--- DATA TYPES ---")
print(df.dtypes)

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- BASIC STATISTICS ---")
print(df.describe(include="all"))


print("\n--- DATA QUALITY CHECKS ---")

print("Cancelled invoices:",
      df["InvoiceNo"].astype(str).str.startswith("C").sum())

print("Negative quantities:",
      (df["Quantity"] < 0).sum())

print("Zero or negative prices:",
      (df["UnitPrice"] <= 0).sum())

print("Unique invoice numbers:",
      df["InvoiceNo"].nunique())
