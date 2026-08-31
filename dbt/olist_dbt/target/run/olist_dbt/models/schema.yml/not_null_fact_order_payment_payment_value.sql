
    
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select payment_value
from `DataEngineeringDB`.`fact_order_payment`
where payment_value is null



  
  
    ) dbt_internal_test