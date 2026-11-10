select
    seller_id,
    seller_zip_code_prefix,
    lower(seller_city) as seller_city,
    upper(seller_state) as seller_state
from {{ source('bronze', 'sellers') }}
