
  
    
    
    
        
         


        insert into `DataEngineeringDB`.`dim_product__dbt_backup`
        ("product_id", "product_category_name", "product_category_name_english", "product_name_lenght", "product_description_lenght", "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm")SELECT
    p.product_id,
    p.product_category_name,
    t.product_category_name_english,
    p.product_name_lenght,
    p.product_description_lenght,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM DataEngineeringDB.stg_products AS p

LEFT JOIN DataEngineeringDB.stg_product_category_translation AS t
    ON p.product_category_name = t.product_category_name
  