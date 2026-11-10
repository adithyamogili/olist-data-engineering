from datetime import datetime, timedelta
import os
import subprocess
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_SRC = "/opt/airflow/src"
DBT_DIR = os.getenv("DBT_PROJECT_DIR", "/opt/airflow/dbt/olist_warehouse")
ENV = os.environ.copy()
ENV["PYTHONPATH"] = PROJECT_SRC + os.pathsep + ENV.get("PYTHONPATH", "")

def run_python(module):
    subprocess.run([sys.executable, "-m", module], check=True, env=ENV)

def run_dbt(command):
    subprocess.run(
        ["dbt", command, "--project-dir", DBT_DIR, "--profiles-dir", DBT_DIR],
        check=True, env=ENV, timeout=60 * 60,
    )

default_args = {
    "owner": "data-engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
    "retry_exponential_backoff": True,
    "execution_timeout": timedelta(hours=2),
}

with DAG(
    dag_id="olist_ecommerce_pipeline",
    description="Bronze ingestion, Silver/Gold dbt transformations and data quality tests",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["olist", "etl", "medallion", "dbt", "postgres"],
) as dag:
    validate = PythonOperator(
        task_id="validate_source_files",
        python_callable=run_python,
        op_args=["olist_pipeline.validate_sources"],
    )
    archive = PythonOperator(
        task_id="optional_archive_to_s3",
        python_callable=run_python,
        op_args=["olist_pipeline.archive_to_s3"],
    )
    ingest = PythonOperator(
        task_id="load_bronze_incrementally",
        python_callable=run_python,
        op_args=["olist_pipeline.load_raw"],
    )
    transform = PythonOperator(task_id="dbt_run_silver_gold", python_callable=run_dbt, op_args=["run"])
    snapshot = PythonOperator(task_id="dbt_snapshot_order_status", python_callable=run_dbt, op_args=["snapshot"])
    test = PythonOperator(task_id="dbt_data_quality_tests", python_callable=run_dbt, op_args=["test"])
    validate >> archive >> ingest >> transform >> snapshot >> test
