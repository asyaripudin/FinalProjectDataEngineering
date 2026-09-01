
  
    
    
    
        
         


        insert into `DataEngineeringDB`.`dim_geolocation__dbt_backup`
        ("geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state")SELECT
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state
FROM DataEngineeringDB.stg_geolocation
  