
    
    

select
    review_id as unique_field,
    count(*) as n_records

from `DataEngineeringDB`.`fact_order_review`
where review_id is not null
group by review_id
having count(*) > 1


