from pathlib import Path
from olist_pipeline.load_raw import sha256_file

def test_sha256_is_stable_and_changes_with_content(tmp_path: Path):
    source = tmp_path / "sample.csv"
    source.write_text("id,value\n1,a\n", encoding="utf-8")
    first = sha256_file(source)
    assert first == sha256_file(source)
    source.write_text("id,value\n1,b\n", encoding="utf-8")
    assert first != sha256_file(source)
