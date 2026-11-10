import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.types import Text

from .config import DATA_DIR, FILES
from .db import get_engine, ensure_control_tables
from .validate_sources import validate_sources
from .logging_config import configure_logging

configure_logging()
LOGGER = logging.getLogger(__name__)

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def _existing_hash(engine, table_name):
    with engine.connect() as conn:
        return conn.execute(
            text("""
                SELECT w.file_sha256
                FROM ops.ingestion_watermarks w
                WHERE w.source_name=:name
                  AND w.load_status='SUCCESS'
                  AND EXISTS (
                    SELECT 1 FROM information_schema.tables t
                    WHERE t.table_schema='bronze' AND t.table_name=:name
                  )
            """),
            {"name": table_name},
        ).scalar_one_or_none()

def _load_file(engine, table_name: str, path: Path, file_hash: str) -> tuple[int, bool]:
    if _existing_hash(engine, table_name) == file_hash:
        LOGGER.info("Skipping unchanged source file: %s", path.name)
        return 0, False

    LOGGER.info("Loading changed source file into bronze.%s", table_name)
    total_rows, first_chunk = 0, True
    temp_table = f"_incoming_{table_name}"
    with engine.begin() as conn:
        conn.execute(text(f'DROP TABLE IF EXISTS bronze."{temp_table}"'))
    try:
        for chunk in pd.read_csv(path, chunksize=25_000):
            chunk.columns = [c.strip().lower() for c in chunk.columns]
            chunk.to_sql(
                temp_table, engine, schema="bronze",
                if_exists="replace" if first_chunk else "append",
                index=False, chunksize=2_000, method="multi",
                dtype={c: Text() for c in chunk.select_dtypes(include="object").columns},
            )
            total_rows += len(chunk)
            first_chunk = False
        if first_chunk:
            raise ValueError(f"Source file is empty: {path}")

        with engine.begin() as conn:
            # Preserve the target table's object identity (OID), so dependent
            # Silver views remain valid when a source snapshot is reloaded.
            target_exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema='bronze' AND table_name=:name
                )
            """), {"name": table_name}).scalar_one()
            if target_exists:
                conn.execute(text(f'TRUNCATE TABLE bronze."{table_name}"'))
                conn.execute(text(
                    f'INSERT INTO bronze."{table_name}" SELECT * FROM bronze."{temp_table}"'
                ))
                conn.execute(text(f'DROP TABLE bronze."{temp_table}"'))
            else:
                conn.execute(text(f'ALTER TABLE bronze."{temp_table}" RENAME TO "{table_name}"'))
            conn.execute(text("""
                INSERT INTO ops.ingestion_watermarks
                    (source_name,file_name,file_sha256,row_count,loaded_at,load_status)
                VALUES (:name,:file,:hash,:rows,now(),'SUCCESS')
                ON CONFLICT (source_name) DO UPDATE SET
                    file_name=EXCLUDED.file_name,file_sha256=EXCLUDED.file_sha256,
                    row_count=EXCLUDED.row_count,loaded_at=now(),load_status='SUCCESS'
            """), {"name":table_name,"file":path.name,"hash":file_hash,"rows":total_rows})
        return total_rows, True
    except Exception:
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS bronze."{temp_table}"'))
            conn.execute(text("""
                INSERT INTO ops.ingestion_watermarks
                    (source_name,file_name,file_sha256,row_count,loaded_at,load_status)
                VALUES (:name,:file,:hash,0,now(),'FAILED')
                ON CONFLICT (source_name) DO UPDATE SET
                    file_sha256=EXCLUDED.file_sha256,loaded_at=now(),load_status='FAILED'
            """), {"name":table_name,"file":path.name,"hash":file_hash})
        raise

def load_raw(data_dir: Path = DATA_DIR):
    validate_sources(data_dir)
    engine = get_engine()
    ensure_control_tables(engine)
    started = datetime.now(timezone.utc)
    total_rows, changed = 0, []
    try:
        for table_name, filename in FILES.items():
            path = data_dir / filename
            rows, did_change = _load_file(engine, table_name, path, sha256_file(path))
            total_rows += rows
            if did_change:
                changed.append(table_name)
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO ops.pipeline_runs
                  (pipeline_name,started_at,finished_at,status,rows_loaded,details)
                VALUES ('olist_ingestion',:started,now(),'SUCCESS',:rows,CAST(:details AS jsonb))
            """), {"started":started,"rows":total_rows,
                    "details":json.dumps({"changed_sources":changed})})
        LOGGER.info("Ingestion completed rows_loaded=%s changed_sources=%s", total_rows, changed)
        return {"rows_loaded":total_rows,"changed_sources":changed}
    except Exception as exc:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO ops.pipeline_runs
                  (pipeline_name,started_at,finished_at,status,details)
                VALUES ('olist_ingestion',:started,now(),'FAILED',CAST(:details AS jsonb))
            """), {"started":started,"details":json.dumps({"error":str(exc)})})
        LOGGER.exception("Ingestion failed")
        raise

if __name__ == "__main__":
    load_raw()
