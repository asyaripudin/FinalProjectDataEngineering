{{ config(
    materialized='table',
    alias='silver_fact_order_payments',
    engine='MergeTree()',
    order_by='(order_id, payment_sequential)',
    settings={'allow_nullable_key': 1}
) }}

WITH source AS (
    SELECT * FROM {{ source('staging', 'stg_fact_order_payments') }}
),

cleaned AS (
    SELECT
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        CASE
            WHEN payment_value IS NULL OR payment_value < 0 THEN 0
            ELSE payment_value
        END AS payment_value
    FROM source
)

SELECT * FROM cleaned