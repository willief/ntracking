#!/bin/bash

# Define log file and its directory
LOG_DIR="$HOME"

# Delete log files older than 3 days
find "$LOG_DIR" -name "resources_*.log" -type f -mtime +3 -exec rm {} \;

