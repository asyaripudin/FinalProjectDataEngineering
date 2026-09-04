{{ config(
    materialized='table',
    alias='silver_dim_geolocation',
    engine='MergeTree()',
    order_by='geolocation_zip_code_prefix',
    settings={'allow_nullable_key': 1}
) }}

WITH source AS (
    SELECT *
    FROM {{ source('staging', 'stg_dim_geolocation') }}
),
cleaned AS (
    SELECT
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        TRIM(INITCAP(geolocation_city)) AS geolocation_city,
        UPPER(TRIM(geolocation_state)) AS geolocation_state
    FROM source
)
SELECT *
FROM cleaned





