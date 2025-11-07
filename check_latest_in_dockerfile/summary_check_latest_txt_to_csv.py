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

# Prepare CSV headers
headers = [
    "Process",
    "Total project",
    "Project using latest",
    "Total Dockerfile",
    "Dockerfile using latest",
    "File not found or error",
    "Repo not found"
]

# Open CSV for writing
with open(output_file, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()

    for block in blocks:
        # Extract data using regex
        data = {
            "Process": re.search(r"Process\s+(\d+)", block).group(1),
            "Total project": re.search(r"Total project:\s*(\d+)", block).group(1),
            "Project using latest": re.search(r"Project using latest:\s*(\d+)", block).group(1),
            "Total Dockerfile": re.search(r"Total Dockerfile:\s*(\d+)", block).group(1),
            "Dockerfile using latest": re.search(r"Dockerfile using latest:\s*(\d+)", block).group(1),
            "File not found or error": re.search(r"File not found or error:\s*(\d+)", block).group(1),
            "Repo not found": re.search(r"Repo not found:\s*(\d+)", block).group(1),
        }
        writer.writerow(data)

print(f"Conversion complete! Data saved to '{output_file}'")
