from pathlib import Path
import pandas as pd
from .logging_config import configure_logging
from .config import DATA_DIR, FILES, REQUIRED_COLUMNS

configure_logging()

def validate_sources(data_dir: Path = DATA_DIR):
    errors = []
    for table, filename in FILES.items():
        path = data_dir / filename
        if not path.is_file():
            errors.append(f"Missing required file: {path}")
            continue
        try:
            columns = set(pd.read_csv(path, nrows=0).columns)
            missing = REQUIRED_COLUMNS[table] - columns
            if missing:
                errors.append(f"{filename} missing columns: {sorted(missing)}")
        except Exception as exc:
            errors.append(f"Could not read {filename}: {exc}")
    if errors:
        raise ValueError("\n".join(errors))
    return True

if __name__ == "__main__":
    validate_sources()
    print("Source validation passed.")
