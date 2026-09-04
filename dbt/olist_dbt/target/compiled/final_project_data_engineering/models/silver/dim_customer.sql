

WITH source AS (
    SELECT *
    FROM `DataEngineeringDB`.`stg_dim_customer`
),
cleaned AS (
    SELECT
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        TRIM(INITCAP(customer_city)) AS customer_city,
        UPPER(TRIM(customer_state)) AS customer_state
    FROM source
)
SELECT *
FROM cleaned