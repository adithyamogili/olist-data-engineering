{{ config(materialized='incremental', unique_key='order_id', incremental_strategy='delete+insert') }}
with item_totals as (
    select order_id, count(*) as item_count,
           sum(item_price) as merchandise_amount, sum(freight_value) as freight_amount
    from {{ ref('stg_order_items') }} group by order_id
),
payment_totals as (
    select order_id, sum(payment_value) as payment_amount,
           max(payment_installments) as max_payment_installments
    from {{ ref('stg_order_payments') }} group by order_id
),
review_scores as (
    select order_id, avg(review_score::numeric) as avg_review_score
    from {{ ref('stg_order_reviews') }} group by order_id
),
base as (
    select o.order_id, o.customer_id, o.order_status, o.order_purchase_at,
        o.order_approved_at, o.order_delivered_carrier_at,
        o.order_delivered_customer_at, o.order_estimated_delivery_at,
        coalesce(i.item_count, 0) as item_count,
        coalesce(i.merchandise_amount, 0) as merchandise_amount,
        coalesce(i.freight_amount, 0) as freight_amount,
        coalesce(p.payment_amount, 0) as payment_amount,
        p.max_payment_installments, r.avg_review_score,
        case when o.order_delivered_customer_at is null or o.order_estimated_delivery_at is null then null
             when o.order_delivered_customer_at <= o.order_estimated_delivery_at then true else false end as delivered_on_time,
        case when o.order_delivered_customer_at is not null
             then extract(epoch from (o.order_delivered_customer_at - o.order_purchase_at)) / 86400.0
             else null end as delivery_days
    from {{ ref('stg_orders') }} o
    left join item_totals i on o.order_id = i.order_id
    left join payment_totals p on o.order_id = p.order_id
    left join review_scores r on o.order_id = r.order_id
)
select * from base
{% if is_incremental() %}
where order_purchase_at >= (
    select coalesce(max(order_purchase_at), timestamp '1900-01-01') - interval '{{ var("incremental_lookback_days", 30) }} days' from {{ this }}
)
{% endif %}
