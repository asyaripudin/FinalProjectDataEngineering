

WITH source AS (
    SELECT * FROM `DataEngineeringDB`.`stg_fact_order_payments`
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