import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data" / "raw"))
FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}
REQUIRED_COLUMNS = {
    "customers": {"customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"},
    "geolocation": {"geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng"},
    "order_items": {"order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"},
    "order_payments": {"order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"},
    "order_reviews": {"review_id", "order_id", "review_score"},
    "orders": {"order_id", "customer_id", "order_status", "order_purchase_timestamp"},
    "products": {"product_id", "product_category_name"},
    "sellers": {"seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"},
    "category_translation": {"product_category_name", "product_category_name_english"},
}
PRIMARY_KEYS = {
    "customers": ["customer_id"],
    "order_items": ["order_id", "order_item_id"],
    "order_payments": ["order_id", "payment_sequential"],
    "order_reviews": ["review_id"],
    "orders": ["order_id"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "category_translation": ["product_category_name"],
    "geolocation": ["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng"],
}
