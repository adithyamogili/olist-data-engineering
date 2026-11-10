-- depends_on: {{ ref('fct_orders') }}
{{ config(materialized='incremental', unique_key=['order_id', 'order_item_id'], incremental_strategy='delete+insert') }}
select oi.order_id, oi.order_item_id, oi.product_id, oi.seller_id,
       oi.shipping_limit_at, oi.item_price, oi.freight_value,
       oi.item_price + oi.freight_value as item_total
from {{ ref('stg_order_items') }} oi
{% if is_incremental() %}
where oi.order_id in (
    select o.order_id
    from {{ ref('fct_orders') }} o
    where o.order_purchase_at >= (
        select coalesce(max(o_existing.order_purchase_at), timestamp '1900-01-01') - interval '{{ var("incremental_lookback_days", 30) }} days'
        from {{ this }} existing_items
        join {{ ref('fct_orders') }} o_existing using (order_id)
    )
)
{% endif %}
