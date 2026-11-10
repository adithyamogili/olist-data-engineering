select order_id from {{ ref('fct_orders') }}
where merchandise_amount < 0 or freight_amount < 0 or payment_amount < 0 or item_count < 0
