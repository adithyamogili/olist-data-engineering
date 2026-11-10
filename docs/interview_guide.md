# Junior Data Engineer interview guide

Use this guide after running the project. Be ready to explain decisions, limitations and failure cases honestly.

## 1. Explain the project in 60 seconds

"I built a batch data platform around the Olist e-commerce dataset. Python validates nine CSV source files and loads them in chunks into PostgreSQL Bronze tables. SHA-256 file fingerprints act as file-level watermarks so unchanged files are skipped and changed snapshots are safely reloaded. dbt builds typed Silver views and Gold dimensions and facts. The order facts use incremental models with a 30-day lookback, and a dbt snapshot tracks changes to order status and delivery fields across runs. Airflow orchestrates the tasks, dbt tests validate data quality, and GitHub Actions runs Python tests and dbt parsing."

Only say this after you've executed and verified each part.

## 2. Core concepts

### ETL vs ELT
- ETL transforms before loading into the destination.
- ELT loads source data first, then transforms inside the warehouse.
- This project is closer to ELT: Python validates and loads source-shaped data; dbt performs warehouse transformations.

### Bronze / Silver / Gold
- Bronze preserves source-shaped data for traceability.
- Silver standardizes types and column semantics.
- Gold exposes business-friendly facts and dimensions.

### Fact vs dimension
- A fact table stores measurable business events at a declared grain.
- A dimension stores descriptive attributes used to filter and group facts.
- Always define grain before writing joins or aggregations.

### Why aggregate before joining?
Orders have multiple items and can have multiple payment rows. Joining both raw child tables can multiply rows. Aggregate each child relation to order grain first, then join the aggregates.

### Idempotency
An operation is idempotent when repeating it with the same inputs produces the same intended state without duplicate side effects. Here, successful source file hashes are recorded; identical files are skipped, and changed snapshot files replace the corresponding table.

### Watermark
A watermark records progress. This project has two related forms:
- SHA-256 file fingerprint for snapshot-file change detection.
- Event-time lookback in dbt incremental facts.

This is not row-level CDC. Explain that limitation clearly.

### Incremental model
An incremental model processes a subset of source data after the first build. A unique key and delete+insert strategy replace matching recent records. A bounded lookback handles late-arriving updates within that period.

### dbt snapshot
A snapshot stores prior versions of records when configured columns change. It cannot reconstruct changes that never appear in the source between runs.

### Airflow
Airflow schedules and monitors task dependencies. It is not the transformation engine; it orchestrates Python and dbt commands.

## 3. Likely interview questions

1. What happens if the same CSV is processed twice?
2. What happens if a file changes after a successful load?
3. Why use a temporary table before replacing a Bronze table?
4. What happens if ingestion fails halfway through?
5. What is the difference between a file fingerprint and an event-time watermark?
6. Why is a 30-day lookback used? What are its limitations?
7. How would you handle a correction from six months ago?
8. What is the grain of `fct_orders` and `fct_order_items`?
9. Why can joining two one-to-many child tables inflate revenue?
10. What is the difference between a fact and a dimension?
11. Why use dbt instead of writing all transformations in Python?
12. What does Airflow retry? What should be idempotent before enabling retries?
13. What does a dbt snapshot do?
14. What is the difference between a dbt test and a Python unit test?
15. How would you secure AWS credentials?
16. How would you extend this to Kafka or CDC?
17. How would you partition a large fact table?
18. How would you monitor freshness and pipeline SLAs?

## 4. Debugging scenarios to practise

- **Duplicate fact rows:** inspect model grain, unique keys and join cardinality.
- **Inflated GMV:** aggregate order items before joining payment rows.
- **Stale historical values:** inspect incremental lookback and run a backfill/full refresh.
- **Airflow retry duplicates:** ensure ingestion and transformations are idempotent.
- **Missing source table:** inspect the Bronze load and dbt source schema.
- **Failed source file:** inspect watermark status and task logs; retry after fixing the cause.
- **S3 access denied:** check bucket, region, endpoint, IAM policy and credentials.

## 5. Practical extensions

After you understand this implementation, add one at a time:
- CDC or API ingestion.
- Parquet conversion and partitioned S3 paths.
- Spark for larger-scale transformations.
- Kafka for order event streaming.
- A dashboard over Gold tables.
- Data freshness and SLA alerting.

Do not add tools to the resume until you have built and explained a working feature with them.
