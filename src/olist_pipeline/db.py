import os
from sqlalchemy import create_engine, text

def get_engine():
    user = os.getenv("WAREHOUSE_USER", "olist")
    password = os.getenv("WAREHOUSE_PASSWORD", "olist_local_password")
    host = os.getenv("WAREHOUSE_HOST", "localhost")
    port = os.getenv("WAREHOUSE_PORT", "5433")
    database = os.getenv("WAREHOUSE_DB", "olist")
    return create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
        pool_pre_ping=True, pool_recycle=1800,
    )

def ensure_control_tables(engine):
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS bronze"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ops"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ops.ingestion_watermarks (
                source_name text PRIMARY KEY, file_name text NOT NULL,
                file_sha256 text NOT NULL, row_count bigint NOT NULL,
                loaded_at timestamptz NOT NULL DEFAULT now(),
                load_status text NOT NULL CHECK (load_status IN ('SUCCESS','FAILED'))
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ops.pipeline_runs (
                run_id bigserial PRIMARY KEY, pipeline_name text NOT NULL,
                started_at timestamptz NOT NULL, finished_at timestamptz,
                status text NOT NULL, rows_loaded bigint NOT NULL DEFAULT 0,
                details jsonb NOT NULL DEFAULT '{}'::jsonb
            )
        """))
