import pandas as pd
import pytest
from olist_pipeline.config import FILES, REQUIRED_COLUMNS
from olist_pipeline.validate_sources import validate_sources

def test_validate_sources_accepts_all_required_headers(tmp_path):
    for table, filename in FILES.items():
        pd.DataFrame(columns=sorted(REQUIRED_COLUMNS[table])).to_csv(tmp_path / filename, index=False)
    assert validate_sources(tmp_path) is True

def test_validate_sources_reports_missing_columns(tmp_path):
    for table, filename in FILES.items():
        columns = sorted(REQUIRED_COLUMNS[table])
        pd.DataFrame(columns=columns if table != "orders" else ["order_id"]).to_csv(tmp_path / filename, index=False)
    with pytest.raises(ValueError, match="missing columns"):
        validate_sources(tmp_path)
