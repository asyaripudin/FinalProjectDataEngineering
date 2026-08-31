
  
    
    
    
        
         


        insert into `DataEngineeringDB`.`dim_seller__dbt_tmp`
        ("seller_id", "seller_zip_code_prefix", "seller_city", "seller_state")SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM DataEngineeringDB.stg_sellers
  