# Changelog

## Version 2.0.0
- Corrected dbt custom schema macro placement and exact Silver/Gold schema naming.
- Introduced Bronze/Silver/Gold medallion layers.
- Added SHA-256 file-level watermarks, chunked temporary-table ingestion, idempotent skip behavior and failed-load retry handling.
- Added incremental Gold facts with configurable event-time lookback.
- Added dbt order-status snapshot and business-rule tests.
- Added JSON structured Python logs and operational run/watermark tables.
- Added optional AWS S3 archival and MinIO local testing.
- Improved Airflow Compose topology with a persistent PostgreSQL metadata database, separate scheduler/webserver and retries.
- Added GitHub Actions CI, architecture, troubleshooting and interview documentation.
