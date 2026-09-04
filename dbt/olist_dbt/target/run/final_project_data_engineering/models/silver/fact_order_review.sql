
  
    
    
    
        
         


        insert into `DataEngineeringDB`.`silver_fact_reviews__dbt_backup`
        ("review_id", "order_id", "review_score", "review_comment_title", "review_comment_message", "review_creation_date", "review_answer_timestamp")

WITH source AS (
    SELECT * FROM `DataEngineeringDB`.`stg_fact_order_reviews`
),

cleaned AS (
    SELECT
        review_id,
        order_id,
        -- Skor review: pastikan dalam rentang 1-5
        CASE
            WHEN review_score < 1 THEN 1
            WHEN review_score > 5 THEN 5
            ELSE review_score
        END AS review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date,
        review_answer_timestamp
    FROM source
)

SELECT * FROM cleaned
  