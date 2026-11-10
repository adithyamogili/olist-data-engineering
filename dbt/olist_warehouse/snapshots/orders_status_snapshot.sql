{% snapshot orders_status_snapshot %}
{{
    config(
      target_schema='silver',
      unique_key='order_id',
      strategy='check',
      check_cols=['order_status', 'order_delivered_customer_at', 'order_estimated_delivery_at']
    )
}}
select order_id, order_status, order_delivered_customer_at, order_estimated_delivery_at
from {{ ref('stg_orders') }}
{% endsnapshot %}
