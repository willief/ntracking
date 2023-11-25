#!/bin/bash

# Base directory for logs
BASE_LOG_DIR="/home/wyse/ntracking/logs"

# Loop through each machine
for machine in wyse wyse1 wyse2 wyse3 wyse4; do
    # Define the source directory and the merged log file name
    LOG_DIR="$BASE_LOG_DIR/$machine"
    MERGED_LOG="/home/wyse/ntracking/resources${machine#wyse}.log" # e.g., resources1.log for wyse1

    # Find, sort, and concatenate logs from the last 7 days into the merged log file
    find "$LOG_DIR" -name 'resources_*.log' -mtime -7 -print0 | sort -z | xargs -0 cat > "$MERGED_LOG"
done

