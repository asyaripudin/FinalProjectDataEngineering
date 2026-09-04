
  
    
    
    
        
         


        insert into `DataEngineeringDB`.`silver_dim_customer__dbt_backup`
        ("customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state")

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
  