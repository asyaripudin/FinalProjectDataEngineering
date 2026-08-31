
  
    
    
    
        
         


        insert into `DataEngineeringDB`.`fact_order_item__dbt_backup`
        ("order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value", "item_total_value")SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,

    parseDateTimeBestEffortOrNull(shipping_limit_date)
        AS shipping_limit_date,

    price,
    freight_value,

    price + freight_value AS item_total_value

FROM DataEngineeringDB.stg_order_items
  