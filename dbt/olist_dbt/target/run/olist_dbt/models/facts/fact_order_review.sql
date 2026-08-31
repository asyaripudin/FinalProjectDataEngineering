
  
    
    
    
        
         


        insert into `DataEngineeringDB`.`fact_order_review__dbt_backup`
        ("review_id", "order_id", "review_score", "review_comment_title", "review_comment_message", "review_creation_date", "review_answer_timestamp")SELECT
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,

    parseDateTimeBestEffortOrNull(review_creation_date)
        AS review_creation_date,

    parseDateTimeBestEffortOrNull(review_answer_timestamp)
        AS review_answer_timestamp

FROM DataEngineeringDB.stg_order_reviews
  