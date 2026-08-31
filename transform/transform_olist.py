import clickhouse_connect

# ============================================================
# CONNECTION CLICKHOUSE
# ============================================================

client = clickhouse_connect.get_client(
    host="localhost",
    port=8124,
    username="admin",
    password="ClickHouse@2026",
    database="DataEngineeringDB"
)

# ============================================================
# HELPER FUNCTION
# ============================================================

def execute(sql):
    client.command(sql)

# ============================================================
# DATABASE
# ============================================================

execute("""
CREATE DATABASE IF NOT EXISTS DataEngineeringDB
""")

# ============================================================
# 1. DIM CUSTOMER
# ============================================================

print("Creating dim_customer...")

execute("""
DROP TABLE IF EXISTS dim_customer
""")

execute("""
CREATE TABLE dim_customer
ENGINE = MergeTree
ORDER BY customer_id
AS
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM stg_customers
""")

# ============================================================
# 2. DIM PRODUCT
# ============================================================

print("Creating dim_product...")

execute("""
DROP TABLE IF EXISTS dim_product
""")

execute("""
CREATE TABLE dim_product
ENGINE = MergeTree
ORDER BY product_id
AS
SELECT
    p.product_id,
    p.product_category_name,
    t.product_category_name_english,
    p.product_name_lenght,
    p.product_description_lenght,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM stg_products p
LEFT JOIN stg_product_category_translation t
    ON p.product_category_name = t.product_category_name
""")

# ============================================================
# 3. DIM SELLER
# ============================================================

print("Creating dim_seller...")

execute("""
DROP TABLE IF EXISTS dim_seller
""")

execute("""
CREATE TABLE dim_seller
ENGINE = MergeTree
ORDER BY seller_id
AS
SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM stg_sellers
""")

# ============================================================
# 4. DIM GEOLOCATION
# ============================================================

print("Creating dim_geolocation...")

execute("""
DROP TABLE IF EXISTS dim_geolocation
""")

execute("""
CREATE TABLE dim_geolocation
ENGINE = MergeTree
ORDER BY geolocation_zip_code_prefix
AS
SELECT
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state
FROM stg_geolocation
""")

# ============================================================
# 5. FACT ORDER
# ============================================================

print("Creating fact_order...")

execute("""
DROP TABLE IF EXISTS fact_order
""")

execute("""
CREATE TABLE fact_order
ENGINE = MergeTree
ORDER BY order_id
AS
SELECT
    order_id,
    customer_id,
    order_status,

    parseDateTimeBestEffortOrNull(order_purchase_timestamp)
        AS order_purchase_timestamp,

    parseDateTimeBestEffortOrNull(order_approved_at)
        AS order_approved_at,

    parseDateTimeBestEffortOrNull(order_delivered_carrier_date)
        AS order_delivered_carrier_date,

    parseDateTimeBestEffortOrNull(order_delivered_customer_date)
        AS order_delivered_customer_date,

    parseDateTimeBestEffortOrNull(order_estimated_delivery_date)
        AS order_estimated_delivery_date

FROM stg_orders
""")

# ============================================================
# 6. FACT ORDER ITEM
# ============================================================

print("Creating fact_order_item...")

execute("""
DROP TABLE IF EXISTS fact_order_item
""")

execute("""
CREATE TABLE fact_order_item
ENGINE = MergeTree
ORDER BY (order_id, order_item_id)
AS
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,

    parseDateTimeBestEffortOrNull(shipping_limit_date)
        AS shipping_limit_date,

    price,
    freight_value

FROM stg_order_items
""")

# ============================================================
# 7. FACT ORDER PAYMENT
# ============================================================

print("Creating fact_order_payment...")

execute("""
DROP TABLE IF EXISTS fact_order_payment
""")

execute("""
CREATE TABLE fact_order_payment
ENGINE = MergeTree
ORDER BY (order_id, payment_sequential)
AS
SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
FROM stg_order_payments
""")

# ============================================================
# 8. FACT ORDER REVIEW
# ============================================================

print("Creating fact_order_review...")

execute("""
DROP TABLE IF EXISTS fact_order_review
""")

execute("""
CREATE TABLE fact_order_review
ENGINE = MergeTree
ORDER BY (order_id, review_id)
AS
SELECT
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,

    parseDateTimeBestEffortOrNull(review_creation_date)
        AS review_creation_date,

    parseDateTimeBestEffortOrNull(review_answer_timestamp)
        AS review_answer_timestamp

FROM stg_order_reviews
""")

# ============================================================
# VALIDATION
# ============================================================

print()
print("=" * 70)
print("TRANSFORM COMPLETED")
print("=" * 70)

tables = [
    "dim_customer",
    "dim_product",
    "dim_seller",
    "dim_geolocation",
    "fact_order",
    "fact_order_item",
    "fact_order_payment",
    "fact_order_review"
]

for table in tables:

    result = client.query(
        f"SELECT count() FROM {table}"
    )

    count = result.result_rows[0][0]

    print(f"{table:<35} {count:>12,} rows")

client.close()

print("=" * 70)

