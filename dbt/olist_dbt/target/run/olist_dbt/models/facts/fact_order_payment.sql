
  
    
    
    
        
         


        insert into `DataEngineeringDB`.`fact_order_payment__dbt_backup`
        ("order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value")SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
FROM DataEngineeringDB.stg_order_payments
  