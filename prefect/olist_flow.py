from prefect import flow, task
import subprocess
import sys
from pathlib import Path

# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXTRACT_SCRIPT = PROJECT_ROOT / "extract" / "extract_olist.py"
LOAD_SCRIPT = PROJECT_ROOT / "load" / "load_olist.py"
DBT_PROJECT = PROJECT_ROOT / "dbt" / "olist_dbt"

# ============================================================
# TASK 1 - EXTRACT
# ============================================================

@task(
    name="Extract Olist CSV",
    retries=2,
    retry_delay_seconds=10
)
def extract_olist():
    print("=" * 70)
    print("START TASK: EXTRACT OLIST DATASET")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, str(EXTRACT_SCRIPT)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Extract process failed.")

    print("=" * 70)
    print("EXTRACT SUCCESS")
    print("=" * 70)

# ============================================================
# TASK 2 - LOAD TO CLICKHOUSE
# ============================================================

@task(
    name="Load Olist to ClickHouse",
    retries=2,
    retry_delay_seconds=10
)
def load_olist():
    print("=" * 70)
    print("START TASK: LOAD OLIST DATASET")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, str(LOAD_SCRIPT)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Load process failed.")

    print("=" * 70)
    print("LOAD SUCCESS")
    print("=" * 70)

# ============================================================
# TASK 3 - DBT RUN
# stg -> dim/fact
# ============================================================

@task(
    name="DBT Run",
    retries=2,
    retry_delay_seconds=10
)
def dbt_run():
    print("=" * 70)
    print("START TASK: DBT RUN")
    print("=" * 70)

    result = subprocess.run(
        ["dbt", "run"],
        cwd=str(DBT_PROJECT),
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("dbt run failed.")

    print("=" * 70)
    print("DBT RUN SUCCESS")
    print("=" * 70)

# ============================================================
# TASK 4 - DBT TEST
# ============================================================

@task(
    name="DBT Test",
    retries=1,
    retry_delay_seconds=10
)
def dbt_test():
    print("=" * 70)
    print("START TASK: DBT TEST")
    print("=" * 70)

    result = subprocess.run(
        ["dbt", "test"],
        cwd=str(DBT_PROJECT),
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("dbt test failed.")

    print("=" * 70)
    print("DBT TEST SUCCESS")
    print("=" * 70)


# ============================================================
# PREFECT FLOW
# ============================================================

@flow(
    name="Olist ETL Pipeline",
    description="Olist ETL pipeline using Python, ClickHouse, dbt and Prefect"
)
def olist_pipeline():

    # 1. Extract CSV
    extract_olist()

    # 2. Load CSV -> ClickHouse staging
    load_olist()

    # 3. Transform staging -> dimension/fact
    dbt_run()

    # 4. Data quality testing
    dbt_test()

# ============================================================
# RUN FLOW
# ============================================================

if __name__ == "__main__":
    olist_pipeline()
