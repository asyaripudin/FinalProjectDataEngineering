{{ config(
    materialized='table',
    alias='silver_dim_sellers',
    engine='MergeTree()',
    order_by='seller_id',
    settings={'allow_nullable_key': 1}
) }}

WITH source AS (
    SELECT * FROM {{ source('staging', 'stg_dim_sellers') }}
),

cleaned AS (
    SELECT
        seller_id,
        seller_zip_code_prefix,
        TRIM(INITCAP(seller_city)) AS seller_city,
        UPPER(TRIM(seller_state)) AS seller_state
    FROM source
)

SELECT * FROM cleaned