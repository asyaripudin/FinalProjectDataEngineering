from pathlib import Path
import pandas as pd
import clickhouse_connect
import time

# ============================================================
# PATH PROJECT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / "archive"

# ============================================================
# CONFIGURATION
# ============================================================

CHUNK_SIZE = 10_000

# Refresh transaksi:
# 2017-01-01 sampai sebelum 2018-01-01
START_DATE = "2017-01-01"
END_DATE = "2018-01-01"

# ============================================================
# CLICKHOUSE CONNECTION
# ============================================================

client = clickhouse_connect.get_client(
    host="localhost",
    port=8124,
    username="admin",
    password="ClickHouse@2026",
    database="DataEngineeringDB"
)

# ============================================================
# DATASET MAPPING
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
# MASTER TABLES
# ============================================================

MASTER_UPSERT_TABLES = {
    "stg_customers": "customer_id",
    "stg_products": "product_id",
    "stg_sellers": "seller_id",
    "stg_product_category_translation": "product_category_name",
}

# Geolocation TIDAK di-upsert berdasarkan ZIP karena
# geolocation_zip_code_prefix tidak unik.
GELOCATION_TABLE = "stg_geolocation"

# ============================================================
# HELPER
# ============================================================

def execute_command(sql):
    client.command(sql)


def wait_for_mutation(table_name, timeout=300):
    """
    Menunggu mutation DELETE ClickHouse selesai.
    """

    start_time = time.time()

    while True:

        result = client.query(f"""
            SELECT count()
            FROM system.mutations
            WHERE database = 'DataEngineeringDB'
              AND table = '{table_name}'
              AND is_done = 0
        """)

        running = result.result_rows[0][0]

        if running == 0:
            return

        if time.time() - start_time > timeout:
            raise TimeoutError(
                f"Mutation pada {table_name} belum selesai "
                f"setelah {timeout} detik."
            )

        print(
            f"Waiting mutation {table_name}..."
        )

        time.sleep(2)

# ============================================================
# MASTER UPSERT
# ============================================================

def upsert_master(file_path, table_name, key_column):

    print()
    print("=" * 70)
    print(f"MASTER UPSERT : {table_name}")
    print("=" * 70)

    total_rows = 0

    # --------------------------------------------------------
    # Temporary table khusus untuk proses UPSERT
    # --------------------------------------------------------

    temp_table = f"_tmp_{table_name}"

    # Hapus temporary table jika masih ada
    execute_command(
        f"DROP TABLE IF EXISTS {temp_table}"
    )

    # --------------------------------------------------------
    # Buat temporary table menggunakan struktur tabel master
    # --------------------------------------------------------

    execute_command(f"""
        CREATE TABLE {temp_table}
        AS {table_name}
        ENGINE = MergeTree
        ORDER BY tuple()
    """)

    try:

        # ----------------------------------------------------
        # LOAD CSV KE TEMPORARY TABLE
        # ----------------------------------------------------

        for chunk_number, chunk in enumerate(
            pd.read_csv(
                file_path,
                chunksize=CHUNK_SIZE
            ),
            start=1
        ):

            if chunk.empty:
                continue

            chunk = chunk.dropna(
                subset=[key_column]
            )

            if chunk.empty:
                continue

            client.insert_df(
                table=temp_table,
                df=chunk
            )

            total_rows += len(chunk)

            print(
                f"Chunk {chunk_number}: "
                f"{len(chunk):,} rows loaded to temporary table | "
                f"Total: {total_rows:,}"
            )

        # ----------------------------------------------------
        # DELETE DATA LAMA
        #
        # Tidak menggunakan IN (...)
        # sehingga tidak terkena Max query size.
        # ----------------------------------------------------

        print()
        print(
            f"Deleting existing records from {table_name}..."
        )

        delete_sql = f"""
            ALTER TABLE {table_name}
            DELETE WHERE {key_column} IN
            (
                SELECT {key_column}
                FROM {temp_table}
            )
        """

        execute_command(delete_sql)

        # Tunggu DELETE selesai
        wait_for_mutation(table_name)

        print("Existing matching records deleted.")

        # ----------------------------------------------------
        # INSERT DATA TERBARU
        # ----------------------------------------------------

        print(
            f"Inserting latest records into {table_name}..."
        )

        execute_command(f"""
            INSERT INTO {table_name}
            SELECT *
            FROM {temp_table}
        """)

        print(
            f"MASTER UPSERT COMPLETED : "
            f"{table_name} = {total_rows:,} rows processed"
        )

    finally:

        # ----------------------------------------------------
        # Hapus temporary table
        # ----------------------------------------------------

        execute_command(
            f"DROP TABLE IF EXISTS {temp_table}"
        )


# ============================================================
# FULL REFRESH GEOLOCATION
# ============================================================

def refresh_geolocation(file_path):

    table_name = GELOCATION_TABLE

    print()
    print("=" * 70)
    print("MASTER FULL REFRESH : stg_geolocation")
    print("=" * 70)

    # --------------------------------------------------------
    # TRUNCATE
    # --------------------------------------------------------

    execute_command(
        f"TRUNCATE TABLE {table_name}"
    )

    print("Existing geolocation data cleared.")

    total_rows = 0

    # --------------------------------------------------------
    # LOAD CSV CHUNKS
    # --------------------------------------------------------

    for chunk_number, chunk in enumerate(
        pd.read_csv(
            file_path,
            chunksize=CHUNK_SIZE
        ),
        start=1
    ):

        if chunk.empty:
            continue

        client.insert_df(
            table=table_name,
            df=chunk
        )

        total_rows += len(chunk)

        print(
            f"Chunk {chunk_number}: "
            f"{len(chunk):,} rows inserted | "
            f"Total: {total_rows:,}"
        )

    print()
    print(
        f"MASTER FULL REFRESH COMPLETED : "
        f"{table_name} = {total_rows:,} rows"
    )


# ============================================================
# GET ORDER IDS
# ============================================================

def get_period_order_ids(file_path):

    print()
    print("=" * 70)
    print("COLLECTING ORDER IDS")
    print("=" * 70)

    order_ids = set()

    for chunk_number, chunk in enumerate(
        pd.read_csv(
            file_path,
            chunksize=CHUNK_SIZE
        ),
        start=1
    ):

        if chunk.empty:
            continue

        chunk["order_purchase_timestamp"] = pd.to_datetime(
            chunk["order_purchase_timestamp"],
            errors="coerce"
        )

        filtered = chunk[
            (chunk["order_purchase_timestamp"] >= START_DATE)
            &
            (chunk["order_purchase_timestamp"] < END_DATE)
        ]

        if not filtered.empty:

            order_ids.update(
                filtered["order_id"]
                .astype(str)
                .tolist()
            )

        print(
            f"Chunk {chunk_number}: "
            f"{len(filtered):,} orders in period"
        )

    print()
    print(
        f"Orders in refresh period: "
        f"{len(order_ids):,}"
    )

    return order_ids


# ============================================================
# CREATE TEMP ORDER IDS TABLE
# ============================================================

def create_order_id_temp_table(order_ids):

    temp_table = "_tmp_refresh_order_ids"

    execute_command(
        f"DROP TABLE IF EXISTS {temp_table}"
    )

    execute_command(f"""
        CREATE TABLE {temp_table}
        (
            order_id String
        )
        ENGINE = MergeTree
        ORDER BY order_id
    """)

    # --------------------------------------------------------
    # Insert order_id dalam chunks
    # --------------------------------------------------------

    order_ids_list = list(order_ids)

    for start in range(
        0,
        len(order_ids_list),
        CHUNK_SIZE
    ):

        batch = order_ids_list[
            start:start + CHUNK_SIZE
        ]

        df = pd.DataFrame({
            "order_id": batch
        })

        client.insert_df(
            table=temp_table,
            df=df
        )

        print(
            f"Order ID batch: "
            f"{start + 1:,} - "
            f"{start + len(batch):,}"
        )

    return temp_table

# ============================================================
# REFRESH ORDERS
# ============================================================

def refresh_orders(file_path):

    table_name = "stg_orders"
    date_column = "order_purchase_timestamp"

    print()
    print("=" * 70)
    print("REFRESH TRANSACTION : stg_orders")
    print("=" * 70)

    # --------------------------------------------------------
    # DELETE EXISTING PERIOD
    # --------------------------------------------------------

    print(
        f"Deleting {START_DATE} to before {END_DATE}..."
    )

    delete_sql = f"""
        ALTER TABLE {table_name}
        DELETE WHERE
            parseDateTimeBestEffortOrNull({date_column}) >= '{START_DATE}'
            AND parseDateTimeBestEffortOrNull({date_column}) < '{END_DATE}'
    """

    execute_command(delete_sql)

    print("Waiting mutation stg_orders...")

    wait_for_mutation(table_name)

    print("Existing period deleted.")

    total_rows = 0

    # --------------------------------------------------------
    # READ CSV IN CHUNKS
    # --------------------------------------------------------

    for chunk_number, chunk in enumerate(
        pd.read_csv(
            file_path,
            chunksize=CHUNK_SIZE
        ),
        start=1
    ):

        if chunk.empty:
            continue

        # ----------------------------------------------------
        # TEMPORARY DATE FOR FILTERING
        # ----------------------------------------------------

        date_filter = pd.to_datetime(
            chunk[date_column],
            errors="coerce"
        )

        # ----------------------------------------------------
        # FILTER PERIOD
        # ----------------------------------------------------

        mask = (
            (date_filter >= START_DATE)
            &
            (date_filter < END_DATE)
        )

        chunk = chunk.loc[mask].copy()

        if chunk.empty:
            continue

        # ----------------------------------------------------
        # IMPORTANT
        #
        # stg_orders.order_purchase_timestamp adalah String.
        # Jangan memasukkan Pandas Timestamp ke ClickHouse.
        # ----------------------------------------------------

        chunk[date_column] = chunk[date_column].astype(str)

        # ----------------------------------------------------
        # INSERT CHUNK
        # ----------------------------------------------------

        client.insert_df(
            table=table_name,
            df=chunk
        )

        total_rows += len(chunk)

        print(
            f"Chunk {chunk_number}: "
            f"{len(chunk):,} rows inserted | "
            f"Total: {total_rows:,}"
        )

    print()
    print(
        f"stg_orders completed: "
        f"{total_rows:,} rows"
    )
    
# ============================================================
# REFRESH CHILD TRANSACTION
# ============================================================

def refresh_child_transaction(
    file_path,
    table_name,
    order_ids,
 ):

    print()
    print("=" * 70)
    print(f"REFRESH TRANSACTION : {table_name}")
    print("=" * 70)

    if not order_ids:
        print("No order_id found. Skip.")
        return

    # --------------------------------------------------------
    # Temporary order_id table
    # --------------------------------------------------------

    temp_table = create_order_id_temp_table(
        order_ids
    )

    try:

        # ----------------------------------------------------
        # DELETE berdasarkan JOIN/subquery
        #
        # Tidak membuat IN (...) raksasa.
        # ----------------------------------------------------

        print(
            f"Deleting existing rows from {table_name}..."
        )

        delete_sql = f"""
            ALTER TABLE {table_name}
            DELETE WHERE order_id IN
            (
                SELECT order_id
                FROM {temp_table}
            )
        """

        execute_command(delete_sql)
        print(f"Waiting mutation {table_name}...")
        wait_for_mutation(table_name)
        print(f"Existing rows deleted from {table_name}.")
        total_rows = 0

        # ----------------------------------------------------
        # LOAD CSV CHUNKS
        # ----------------------------------------------------

        for chunk_number, chunk in enumerate(
            pd.read_csv(
                file_path,
                chunksize=CHUNK_SIZE
            ),
            start=1
        ):

            if chunk.empty:
                continue

            chunk["order_id"] = (
                chunk["order_id"]
                .astype(str)
            )

            chunk = chunk[
                chunk["order_id"].isin(order_ids)
            ]

            if chunk.empty:
                continue

            client.insert_df(
                table=table_name,
                df=chunk
            )

            total_rows += len(chunk)

            print(
                f"Chunk {chunk_number}: "
                f"{len(chunk):,} rows inserted | "
                f"Total: {total_rows:,}"
            )

        print()
        print(
            f"{table_name} completed: "
            f"{total_rows:,} rows"
        )

    finally:

        execute_command(
            f"DROP TABLE IF EXISTS {temp_table}"
        )


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print("START OLIST INCREMENTAL LOAD")
print("=" * 70)

print("Database     : DataEngineeringDB")
print(f"Chunk size   : {CHUNK_SIZE:,}")
print(f"Start date   : {START_DATE}")
print(f"End date     : {END_DATE}")
print()

# ============================================================
# FILE PATH
# ============================================================

file_paths = {}

for csv_file, table_name in datasets.items():

    file_path = ARCHIVE_DIR / csv_file

    if not file_path.exists():

        print(
            f"WARNING: File tidak ditemukan: "
            f"{file_path}"
        )

        continue

    file_paths[table_name] = file_path


# ============================================================
# 1. MASTER UPSERT
# ============================================================

print()
print("#" * 70)
print("# STEP 1 - MASTER UPSERT")
print("#" * 70)

for table_name, key_column in MASTER_UPSERT_TABLES.items():

    if table_name not in file_paths:
        continue

    upsert_master(
        file_paths[table_name],
        table_name,
        key_column
    )


# ============================================================
# 1B. GEOLOCATION FULL REFRESH
# ============================================================

print()
print("#" * 70)
print("# STEP 1B - GEOLOCATION FULL REFRESH")
print("#" * 70)

if GELOCATION_TABLE in file_paths:

    refresh_geolocation(
        file_paths[GELOCATION_TABLE]
    )


# ============================================================
# 2. GET ORDER IDS
# ============================================================

print()
print("#" * 70)
print("# STEP 2 - IDENTIFY ORDERS 2024-2026")
print("#" * 70)

order_ids = get_period_order_ids(
    file_paths["stg_orders"]
)


# ============================================================
# 3. REFRESH ORDERS
# ============================================================

print()
print("#" * 70)
print("# STEP 3 - REFRESH ORDERS")
print("#" * 70)

refresh_orders(
    file_paths["stg_orders"]
)


# ============================================================
# 4. REFRESH ORDER ITEMS
# ============================================================

print()
print("#" * 70)
print("# STEP 4 - REFRESH ORDER ITEMS")
print("#" * 70)

refresh_child_transaction(
    file_paths["stg_order_items"],
    "stg_order_items",
    order_ids
)


# ============================================================
# 5. REFRESH ORDER PAYMENTS
# ============================================================

print()
print("#" * 70)
print("# STEP 5 - REFRESH ORDER PAYMENTS")
print("#" * 70)

refresh_child_transaction(
    file_paths["stg_order_payments"],
    "stg_order_payments",
    order_ids
)


# ============================================================
# 6. REFRESH ORDER REVIEWS
# ============================================================

print()
print("#" * 70)
print("# STEP 6 - REFRESH ORDER REVIEWS")
print("#" * 70)

refresh_child_transaction(
    file_paths["stg_order_reviews"],
    "stg_order_reviews",
    order_ids
)


# ============================================================
# 7. FINAL VALIDATION
# ============================================================

print()
print("=" * 70)
print("FINAL STAGING VALIDATION")
print("=" * 70)

for table_name in datasets.values():

    result = client.query(
        f"SELECT count() FROM {table_name}"
    )

    total_rows = result.result_rows[0][0]

    print(
        f"{table_name:<40} "
        f"{total_rows:>12,}"
    )


print()
print("=" * 70)
print("OLIST INCREMENTAL LOAD COMPLETED")
print("=" * 70)