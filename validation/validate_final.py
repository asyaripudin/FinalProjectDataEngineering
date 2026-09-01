import clickhouse_connect
import sys

print("=" * 70)
print("FINAL DATA VALIDATION")
print("=" * 70)

client = clickhouse_connect.get_client(
    host="localhost",
    port=8124,
    username="admin",
    password="ClickHouse@2026",
    database="DataEngineeringDB"
)

tables = [
    ("dim_customer", 99441),
    ("dim_geolocation", 1000163),
    ("dim_product", 32951),
    ("dim_seller", 3095),
    ("fact_order", 99441),
    ("fact_order_item", 112650),
    ("fact_order_payment", 103886),
    ("fact_order_review", 99224),
]

all_valid = True

for table_name, expected_rows in tables:

    query = f"SELECT count() FROM {table_name}"
    actual_rows = client.command(query)

    status = "PASS" if actual_rows == expected_rows else "FAIL"

    print(
        f"{table_name:<35} "
        f"Expected: {expected_rows:<10} "
        f"Actual: {actual_rows:<10} "
        f"[{status}]"
    )

    if actual_rows != expected_rows:
        all_valid = False


print("=" * 70)

if all_valid:
    print("FINAL DATA VALIDATION SUCCESS")
    sys.exit(0)
else:
    print("FINAL DATA VALIDATION FAILED")
    sys.exit(1)