# Troubleshooting guide

## Docker daemon is unavailable

- Start Docker Desktop and wait until the engine is ready.
- Run `docker version` and `docker compose version`.
- On Windows, ensure Docker Desktop is using Linux containers.

## Airflow cannot connect to PostgreSQL metadata DB

- Confirm `warehouse` is healthy: `docker compose ps`.
- Check the `airflow` database exists. The init SQL runs only when the Postgres volume is first initialized.
- If this is a disposable local setup and the DB was initialized before the Airflow DB init script existed, back up anything important before resetting volumes. `docker compose down -v` deletes the local database volume.

## Airflow UI is unavailable

- Inspect logs: `docker compose logs airflow-webserver airflow-scheduler`.
- Check port 8080 is not already in use.
- Confirm `airflow-init` completed successfully.

## Source validation fails

- Ensure all nine exact CSV filenames are in `data/raw/`.
- Do not place the ZIP file itself in `data/raw/`; extract its contents.
- Confirm the files are the original Olist CSVs and their headers have not been renamed.

## Python ingestion fails

- Check Postgres health and `.env` credentials.
- From inside Compose, use host `warehouse` and port `5432`; from the host, use `localhost` and port `5433`.
- Review Airflow task logs. A failed load should not update the watermark to `SUCCESS`.
- If a source file changes, the entire affected Bronze table is intentionally replaced.

## dbt says a source or relation does not exist

- Confirm ingestion completed and `bronze` tables exist.
- Run `dbt debug` and `dbt ls --project-dir ...`.
- Check `dbt/olist_warehouse/models/sources.yml` uses schema `bronze`.
- The custom schema macro must be under `dbt/olist_warehouse/macros/`, not at repository root.
- The configured output schemas are `silver` and `gold`; analytics SQL therefore queries `gold.*`.

## dbt incremental data appears stale

- The facts refresh a 30-day event-time lookback. Historical corrections older than that window require a full refresh.
- Run the full-refresh command in README, then `dbt test`.
- Ensure the changed source CSV was actually reloaded (inspect `ops.ingestion_watermarks`).

## S3 task fails

- Leave `S3_BUCKET` blank to skip the optional archive.
- For MinIO, use `http://minio:9000` from Airflow containers, not `localhost`.
- Ensure the bucket exists and credentials match MinIO.
- For AWS, verify IAM permission, bucket region and prefix.

## GitHub Actions dbt parse fails

- Confirm `dbt-core` and `dbt-postgres` versions match `requirements.txt`.
- Verify the profile env vars are supplied in the workflow.
- `dbt parse` checks project parsing; it does not connect to a live database or prove the pipeline executes end-to-end.
