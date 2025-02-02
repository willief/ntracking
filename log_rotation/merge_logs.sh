#!/bin/bash

# Base directory for logs
BASE_LOG_DIR="$HOME/.local/share/ntracking/logs"

# Loop through each machine
for machine in s00 s01 s02 s03 s04 s05 s06 s07 s08 s09 s10 s11 s12 s13 s14 s15 s16 s17 s18 s19 s20 s21 s22 s23 s24 s25 s26 s27 s28 s29 s30; do
    # Define the source directory and the merged log file name
    LOG_DIR="$BASE_LOG_DIR/$machine"
    MERGED_LOG="$HOME/.local/share/ntracking/resources${machine#s}.log" # e.g., resources1.log for system_01

    # Find, sort, and concatenate logs from the last 7 days into the merged log file
    find "$LOG_DIR" -name 'resources_*.log' -mtime -7 -print0 | sort -z | xargs -0 cat > "$MERGED_LOG"
done

#delete empty files from non existing machines
find $HOME/.local/share/ntracking/ -type f -empty -print -delete
