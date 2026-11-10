select
    review_id,
    order_id,
    cast(review_score as integer) as review_score,
    cast(review_creation_date as timestamp) as review_created_at,
    cast(review_answer_timestamp as timestamp) as review_answered_at
from {{ source('bronze', 'order_reviews') }}
