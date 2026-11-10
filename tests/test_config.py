from olist_pipeline.config import FILES, REQUIRED_COLUMNS, PRIMARY_KEYS

def test_each_source_has_required_columns_and_key():
    assert set(FILES) == set(REQUIRED_COLUMNS) == set(PRIMARY_KEYS)
    assert len(FILES) == 9
    assert all(REQUIRED_COLUMNS[name] for name in FILES)
    assert all(PRIMARY_KEYS[name] for name in FILES)

def test_expected_order_source_is_configured():
    assert FILES["orders"] == "olist_orders_dataset.csv"
    assert {"order_id", "customer_id", "order_status"} <= REQUIRED_COLUMNS["orders"]
