#!/bin/bash

# Define log file and its directory
LOG_DIR="$HOME"

# Define the age limit in days
AGE_LIMIT=2

# Current date in YYYYMMDD format
CURRENT_DATE=$(date +%Y%m%d)

# Delete log files based on date in filename
for file in "$LOG_DIR"/resources_*.log; do
  # Extract the date from the filename
  filename=$(basename "$file")
  file_date=${filename:11:8}

  # Validate and clean the date string
  if [[ $file_date =~ ^[0-9]{8}$ ]]; then
    # Convert file date to a number for comparison
    file_date_number=$(echo $file_date | sed 's/^0*//')  # Remove leading zeros
    current_date_number=$(echo $CURRENT_DATE | sed 's/^0*//')  # Remove leading zeros

    # Calculate the age of the file in days
    file_age=$((current_date_number - file_date_number))

    # Check if the file is older than the age limit
    if [ $file_age -ge $AGE_LIMIT ]; then
      echo "Deleting $file"
      rm "$file"
    fi
  else
    echo "Skipping invalid file: $file"
  fi
done

