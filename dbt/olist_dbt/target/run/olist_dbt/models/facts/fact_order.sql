
  
    
    
    
        
         


        insert into `DataEngineeringDB`.`fact_order__dbt_backup`
        ("order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date")SELECT
    order_id,
    customer_id,
    order_status,

    parseDateTimeBestEffortOrNull(order_purchase_timestamp)
        AS order_purchase_timestamp,

    parseDateTimeBestEffortOrNull(order_approved_at)
        AS order_approved_at,

    parseDateTimeBestEffortOrNull(order_delivered_carrier_date)
        AS order_delivered_carrier_date,

    parseDateTimeBestEffortOrNull(order_delivered_customer_date)
        AS order_delivered_customer_date,

    parseDateTimeBestEffortOrNull(order_estimated_delivery_date)
        AS order_estimated_delivery_date

FROM DataEngineeringDB.stg_orders
  