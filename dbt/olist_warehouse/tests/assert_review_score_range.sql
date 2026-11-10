select order_id, avg_review_score from {{ ref('fct_orders') }}
where avg_review_score is not null and (avg_review_score < 1 or avg_review_score > 5)
