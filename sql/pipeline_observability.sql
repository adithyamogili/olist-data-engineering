-- Source ingestion watermarks: identify unchanged, changed, and failed inputs.
select source_name, file_name, row_count, loaded_at, load_status
from ops.ingestion_watermarks
order by source_name;

-- Recent pipeline run history.
select run_id, pipeline_name, started_at, finished_at, status, rows_loaded, details
from ops.pipeline_runs
order by started_at desc
limit 25;
