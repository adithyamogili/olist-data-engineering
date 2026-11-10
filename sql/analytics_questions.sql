-- 1. Monthly order volume and merchandise GMV
select date_trunc('month', order_purchase_at)::date as month,
       count(*) as orders,
       sum(merchandise_amount) as merchandise_gmv
from gold.fct_orders
group by 1
order by 1;

-- 2. Average order value (merchandise amount, excluding freight)
select avg(merchandise_amount) as average_order_value
from gold.fct_orders
where order_status = 'delivered';

-- 3. On-time delivery rate for delivered orders
select
  count(*) filter (where delivered_on_time is true)::numeric
    / nullif(count(*) filter (where delivered_on_time is not null), 0) as on_time_rate
from gold.fct_orders
where order_status = 'delivered';

-- 4. Revenue by product category
select p.product_category, sum(i.item_price) as merchandise_revenue
from gold.fct_order_items i
join gold.dim_products p using (product_id)
group by 1
order by 2 desc
limit 15;

-- 5. Repeat customer rate based on customer_unique_id
with customer_orders as (
  select c.customer_unique_id, count(*) as order_count
  from gold.fct_orders o
  join gold.dim_customers c using (customer_id)
  group by 1
)
select
  count(*) filter (where order_count > 1)::numeric / count(*) as repeat_customer_rate
from customer_orders;
