from datetime import datetime
import subprocess

# Get current date in yyyy.mm.dd format
date_part = datetime.now().strftime("%Y.%m.%d")

# Get the latest git commit hash
try:
    git_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip().decode("utf-8")
except subprocess.CalledProcessError:
    git_hash = "no_git"  # Fallback if not in a git repository

# Combine the date and git hash
timestamp = f"{date_part}.{git_hash}"

print(timestamp)