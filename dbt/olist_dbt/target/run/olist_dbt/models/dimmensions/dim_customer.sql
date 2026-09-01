
  
    
    
    
        
         


        insert into `DataEngineeringDB`.`dim_customer__dbt_backup`
        ("customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state")SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM DataEngineeringDB.stg_customers
  