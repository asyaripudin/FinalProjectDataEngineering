from pathlib import Path
import pandas as pd
import clickhouse_connect

# ============================================================
# Path Project
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / "archive"

# ============================================================
# Koneksi ke ClickHouse Final Project
# ============================================================

client = clickhouse_connect.get_client(
    host="localhost",
    port=8124,
    username="admin",
    password="ClickHouse@2026",
    database="DataEngineeringDB"
)

# ============================================================
# Mapping CSV → Tabel Staging
# ============================================================

datasets = {
    "olist_customers_dataset.csv": "stg_customers",
    "olist_geolocation_dataset.csv": "stg_geolocation",
    "olist_order_items_dataset.csv": "stg_order_items",
    "olist_order_payments_dataset.csv": "stg_order_payments",
    "olist_order_reviews_dataset.csv": "stg_order_reviews",
    "olist_orders_dataset.csv": "stg_orders",
    "olist_products_dataset.csv": "stg_products",
    "olist_sellers_dataset.csv": "stg_sellers",
    "product_category_name_translation.csv": "stg_product_category_translation",
}

# ============================================================
# Load CSV → ClickHouse
# ============================================================

print("=" * 70)
print("START LOAD OLIST DATASET")
print("=" * 70)

for csv_file, table_name in datasets.items():

    file_path = ARCHIVE_DIR / csv_file

    print()
    print("-" * 70)
    print(f"File       : {csv_file}")
    print(f"Table      : {table_name}")
    print(f"Reading    : {file_path}")

    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if not file_path.exists():
        print(f"ERROR: File tidak ditemukan: {file_path}")
        continue

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    df = pd.read_csv(file_path)

    print(f"Rows       : {len(df):,}")
    print(f"Columns    : {len(df.columns)}")

    # --------------------------------------------------------
    # Clear existing data
    # --------------------------------------------------------

    client.command(f"TRUNCATE TABLE {table_name}")

    print("Existing data cleared.")


    # --------------------------------------------------------
    # Load DataFrame → ClickHouse
    # --------------------------------------------------------

    client.insert_df(
        table=table_name,
        df=df
    )

    # --------------------------------------------------------
    # Validasi jumlah data
    # --------------------------------------------------------

    result = client.query(
        f"SELECT count() FROM {table_name}"
    )

    total_rows = result.result_rows[0][0]

    print(f"Loaded     : {total_rows:,} rows")

print()
print("=" * 70)
print("LOAD OLIST DATASET COMPLETED")
print("=" * 70)
