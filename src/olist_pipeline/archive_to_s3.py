import logging
import os
from pathlib import Path
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from .config import DATA_DIR, FILES
from .logging_config import configure_logging

configure_logging()

LOGGER = logging.getLogger(__name__)

def archive_to_s3(data_dir: Path = DATA_DIR):
    bucket = os.getenv("S3_BUCKET")
    if not bucket:
        LOGGER.info("S3_BUCKET is unset; skipping optional S3 archive step.")
        return {"status": "SKIPPED", "files_uploaded": 0}
    prefix = os.getenv("S3_PREFIX", "olist/bronze/source_files").strip("/")
    client = boto3.client(
        "s3",
        region_name=os.getenv("AWS_DEFAULT_REGION", "ap-south-1"),
        endpoint_url=os.getenv("S3_ENDPOINT_URL") or None,
    )
    uploaded = 0
    try:
        for filename in FILES.values():
            path = data_dir / filename
            client.upload_file(str(path), bucket, f"{prefix}/{filename}")
            uploaded += 1
            LOGGER.info("Archived source file to s3://%s/%s/%s", bucket, prefix, filename)
    except (BotoCoreError, ClientError):
        LOGGER.exception("S3 archival failed")
        raise
    return {"status": "SUCCESS", "files_uploaded": uploaded}

if __name__ == "__main__":
    print(archive_to_s3())
