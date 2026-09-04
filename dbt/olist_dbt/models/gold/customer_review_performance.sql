{{ config(
    materialized='table',
    alias='gold_customer_review_performance',
    engine='MergeTree()',
    order_by='review_score'
) }}

SELECT
    review_score,
    COUNT(*) AS total_reviews,
    ROUND(
        COUNT(*) * 100.0
        / (SELECT COUNT(*)
           FROM {{ ref('fact_order_review') }}
           WHERE review_score IS NOT NULL),
        2
    ) AS review_percentage,

    CASE
        WHEN review_score = 1 THEN 'Sangat Tidak Puas'
        WHEN review_score = 2 THEN 'Tidak Puas'
        WHEN review_score = 3 THEN 'Cukup'
        WHEN review_score = 4 THEN 'Puas'
        WHEN review_score = 5 THEN 'Sangat Puas'
        ELSE 'Tidak Diketahui'
    END AS satisfaction_level

FROM {{ ref('fact_order_review') }}

WHERE review_score IS NOT NULL

GROUP BY review_score
ORDER BY review_score