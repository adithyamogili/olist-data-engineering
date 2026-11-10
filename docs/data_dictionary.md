# Data dictionary

## Models and grain

| Model | Grain | Key |
|---|---|---|
| `gold.dim_customers` | One source customer record | `customer_id` |
| `gold.dim_products` | One product | `product_id` |
| `gold.dim_sellers` | One seller | `seller_id` |
| `gold.fct_orders` | One order | `order_id` |
| `gold.fct_order_items` | One line item in an order | (`order_id`, `order_item_id`) |

## Important measures

- `merchandise_amount`: sum of item prices, excluding freight.
- `freight_amount`: sum of item freight charges.
- `payment_amount`: sum of payment rows for an order.
- `item_count`: number of order-item rows.
- `delivery_days`: elapsed days between purchase and customer delivery.
- `delivered_on_time`: customer delivery timestamp is no later than estimated delivery timestamp.
- `avg_review_score`: average review score for an order where a review exists.

## Operational metadata

`ops.ingestion_watermarks` records each source file's SHA-256, row count, load time and status. `ops.pipeline_runs` records ingestion-level run status, total rows loaded and changed source names or failure details.

## Source notes

The Olist dataset includes customers, geolocation, order items, payments, reviews, orders, products, sellers and product-category translation. Source column names are preserved in Bronze; Silver models standardize types and selected naming.
