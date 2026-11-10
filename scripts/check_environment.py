import shutil
import sys

missing = [tool for tool in ("docker", "git") if shutil.which(tool) is None]
if missing:
    print("Missing tools:", ", ".join(missing))
    sys.exit(1)
print("Docker and Git are available.")
