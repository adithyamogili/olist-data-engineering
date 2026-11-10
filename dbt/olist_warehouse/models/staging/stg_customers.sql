select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    lower(customer_city) as customer_city,
    upper(customer_state) as customer_state
from {{ source('bronze', 'customers') }}
