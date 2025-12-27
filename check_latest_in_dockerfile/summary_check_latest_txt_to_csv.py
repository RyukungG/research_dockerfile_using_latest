import csv
import re

# Input and output file names
input_file = "output/summary_check_latest_in_dockerfile.txt"
output_file = "output/summary_check_latest_in_dockerfile.csv"

# Read the entire text
with open(input_file, "r") as f:
    text = f.read()

# Split text blocks by separator line
blocks = [b.strip() for b in text.split("--------------------------------------------------") if b.strip()]

# Prepare CSV headers (UPDATED)
headers = [
    "Process",
    "Total project",
    "Project using latest",
    "Total Dockerfile",
    "Dockerfile using latest",
    "Number of changes pinned to latest",
    "Number of changes latest to pinned",
    "File not found or error",
    "Repo not found"
]

def extract(pattern, text, default="0"):
    """Safe regex extractor"""
    m = re.search(pattern, text)
    return m.group(1) if m else default

# Open CSV for writing
with open(output_file, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()

    for block in blocks:
        data = {
            "Process": extract(r"Process\s+(\d+)", block),
            "Total project": extract(r"Total project:\s*(\d+)", block),
            "Project using latest": extract(r"Project using latest:\s*(\d+)", block),
            "Total Dockerfile": extract(r"Total Dockerfile:\s*(\d+)", block),
            "Dockerfile using latest": extract(r"Dockerfile using latest:\s*(\d+)", block),
            "Number of changes pinned to latest": extract(
                r"Number of changes pinned to latest:\s*(\d+)", block
            ),
            "Number of changes latest to pinned": extract(
                r"Number of changes latest to pinned:\s*(\d+)", block
            ),
            "File not found or error": extract(r"File not found or error:\s*(\d+)", block),
            "Repo not found": extract(r"Repo not found:\s*(\d+)", block),
        }

        writer.writerow(data)

print(f"Conversion complete! Data saved to '{output_file}'")
