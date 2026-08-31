from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / "archive"

files = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]

for file_name in files:
    file_path = ARCHIVE_DIR / file_name

    print(f"\n{'=' * 60}")
    print(f"File: {file_name}")

    df = pd.read_csv(file_path)

    print(f"Jumlah baris : {len(df):,}")
    print(f"Jumlah kolom : {len(df.columns)}")
    print("Kolom:")
    print(df.columns.tolist())
    print("\nData type:")
    print(df.dtypes)