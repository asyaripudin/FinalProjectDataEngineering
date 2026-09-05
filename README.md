# Olist Data Engineering Pipeline

## 1. Project Overview

Project ini merupakan implementasi **Data Engineering Pipeline** menggunakan dataset **Brazilian E-Commerce Public Dataset by Olist**.

Pipeline dirancang dengan arsitektur **ETL/ELT Bronze–Silver–Gold** untuk melakukan proses extract, load, transformation, data quality testing, dan final data validation secara terotomatisasi.

Pipeline menggunakan **Python, ClickHouse, dbt, dan Prefect**.

---

## 2. Project Objectives

Project ini bertujuan untuk:

* Mengambil data dari dataset Olist.
* Memuat data ke database ClickHouse.
* Melakukan transformasi data menggunakan dbt.
* Membentuk layer Silver dan Gold.
* Melakukan data quality testing menggunakan dbt.
* Melakukan validasi jumlah data pada tabel final.
* Mengorkestrasi seluruh pipeline menggunakan Prefect.

---

## 3. Architecture

```text
                 OLIST CSV DATA
                       │
                       ▼
              ┌─────────────────┐
              │     EXTRACT     │
              │ Python Script   │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │     BRONZE      │
              │ Raw / Staging   │
              └────────┬────────┘
                       ▼
                 ┌───────────┐
                 │ ClickHouse│
                 └─────┬─────┘
                       ▼
              ┌─────────────────┐
              │     SILVER      │
              │ dbt Models      │
              │ Cleaning &      │
              │ Transformation  │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │      GOLD       │
              │ Fact & Dimension│
              │ Tables          │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │   DATA QUALITY  │
              │    dbt test     │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │ FINAL VALIDATION│
              └─────────────────┘
```

---

## 4. Technology Stack

| Technology   | Purpose                                      |
| ------------ | -------------------------------------------- |
| Python       | Extract, load, and validation                |
| ClickHouse   | Analytical database                          |
| dbt          | Data transformation and testing              |
| Prefect      | Workflow orchestration                       |
| PowerShell   | Project execution and environment management |
| Git / GitHub | Version control                              |

---

## 5. Project Structure

FinalProjectDataEngineering
│
├── archive
│   └── transform_olist.py
│
├── bronze
│   └── create_staging_tables.py
│
├── extract
│   └── extract_olist.py
│
├── load
│   └── load_olist.py
│
├── dbt
│   └── olist_dbt
│       ├── macros
│       ├── models
│       │   ├── silver
│       │   └── gold
│       ├── dbt_project.yml
│       └── profiles.yml
│
├── prefect
│   └── pipeline_flow.py
│
├── validation
│   └── validate_final.py
│
├── logs
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 6. Pipeline Process

### Step 1 — Extract

`extract/extract_olist.py`

Mengambil dan mempersiapkan dataset Olist sebagai sumber data pipeline.

### Step 2 — Bronze

`bronze/create_staging_tables.py`

Membuat tabel staging pada ClickHouse untuk menampung data awal sebelum dilakukan transformasi.

### Step 3 — Load

`load/load_olist.py`

Memuat data Olist ke database ClickHouse.

### Step 4 — Silver Transformation

Transformasi data dilakukan menggunakan **dbt** pada:

dbt/olist_dbt/models/silver

Tahap ini digunakan untuk melakukan cleaning dan transformation terhadap data staging.

### Step 5 — Gold Transformation

Model Gold berada pada:


dbt/olist_dbt/models/gold


Layer Gold menghasilkan tabel **fact dan dimension** yang siap digunakan untuk kebutuhan analytical queries.

### Step 6 — Data Quality Testing

dbt menjalankan automated tests untuk memastikan kualitas dan integritas data.

Hasil pengujian:

```text
20 tests passed
0 failed
0 warnings
```

### Step 7 — Final Data Validation

Script:

```text
validation/validate_final.py
```

digunakan untuk membandingkan jumlah data yang diharapkan dengan jumlah data aktual pada tabel final.

Hasil validasi:

```text
dim_customer       : PASS
dim_geolocation    : PASS
dim_product        : PASS
dim_seller         : PASS
fact_order         : PASS
fact_order_item    : PASS
fact_order_payment : PASS
fact_order_review  : PASS
```

---

## 7. Prefect Orchestration

Seluruh proses pipeline diorkestrasi menggunakan Prefect.

Flow:

```text
Extract Olist
      ↓
Load Olist to ClickHouse
      ↓
dbt Run
      ↓
dbt Test
      ↓
Final Data Validation
      ↓
COMPLETED
```

Prefect deployment:

```text
Flow    : Olist ETL Pipeline
Deployment : olist-daily
Work Pool : olist-pool
Schedule : Daily 08:00 WIB
```

---

## 8. Pipeline Result

Pipeline berhasil dijalankan secara end-to-end.

Hasil akhir:

```text
dbt run
13 models passed

dbt test
20 tests passed

Final Data Validation
8 tables validated successfully

Prefect Flow
COMPLETED
```

Dengan demikian, pipeline berhasil melakukan proses **Extract → Load → Transform → Test → Validate** secara otomatis.

---

## 9. How to Run

Aktifkan virtual environment:

```powershell
cd C:\FinalProjectDataEngineering
.\.venv\Scripts\Activate.ps1
```

Jalankan Prefect flow:

```powershell
python .\prefect\pipeline_flow.py
```

Atau pipeline dapat dijalankan melalui Prefect deployment yang telah dikonfigurasi.

Untuk menjalankan dbt secara manual:

```powershell
cd .\dbt\olist_dbt

dbt run
dbt test
```

---

## 10. Conclusion

Project ini mengimplementasikan pipeline data end-to-end menggunakan Python, ClickHouse, dbt, dan Prefect.

Arsitektur Bronze–Silver–Gold digunakan untuk memisahkan data berdasarkan tahap pemrosesan, sedangkan dbt digunakan untuk transformation dan data quality testing.

Prefect digunakan untuk mengorkestrasi seluruh proses sehingga pipeline dapat dijalankan secara terjadwal dan terotomatisasi.










# Mark Down
## Development History:
1. Menambah Folder archive
2. Copy file olist ke folder archive
3. Membuat koneksi ke Cickhouse dengan docker-compose.yml
4. Membuat database DataEngineeringDB di ClickHouse
5. Membuat virtual environment
6. Membuat koneksi ke ClickHouse
7. Membuat models(dimmension & facts)
8. Membuat coding extract_olist.py, creae_staging_tables.py, load_olist.py, transform_olist.py
9. membuat coding dbt_project.yml, schema.yml
10. Install Prefect
11. Membuat coding coding olist_flow.py(extract_olist.py, load_olist, olist_dbt)
12. Run olist_flow.py (EXTRACT, LOAD TO CLICKHOUSE, DBT RUN, DBT TEST)
13. Tambah DBT_EXE pada Configuration
14. Modify result pada dbt_run dan dbt_test
15. Memperbaiki coding load_olist.py (upsert tabel master/dim, chunksize untuk file besar/memory pressure, transaksi/fact, transaksi refresh berdasarkan start_date dan end_date, )
