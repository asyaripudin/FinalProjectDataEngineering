
  
    
    
    
        
         


        insert into `DataEngineeringDB`.`silver_dim_geolocation__dbt_backup`
        ("geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state")

WITH source AS (
    SELECT *
    FROM `DataEngineeringDB`.`stg_dim_geolocation`
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
  