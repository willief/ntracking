#!/bin/bash

# Define the base directory for the safe node data
base_dir="${HOME}/.local/share/safe/node"

# Declare an associative array to store directory names and corresponding PIDs
declare -A dir_pid
node_number=0

# Iterate through directories in the base directory
for dir in "$base_dir"/*; do
  if [[ -f "$dir/safenode.pid" ]]; then
    dir_name=$(basename "$dir")
    dir_pid["$dir_name"]=$(cat "$dir/safenode.pid")
  fi
done

# Loop through directory names and associated PIDs
for dir in "${!dir_pid[@]}"; do
  pid=${dir_pid[$dir]}

  echo "------------------------------------------"
  echo "Local Timestamp: $(date +'%a %b %d %H:%M:%S %Z %Y')"
  echo "Global (UTC) Timestamp: $(TZ='UTC' date +'%a %b %d %H:%M:%S %Z %Y')"
  echo "Number: $node_number"
  echo "Node: $dir"
  echo "PID: $pid"

  # Check if the process is running
  process_info=$(ps -o rss,%cpu -p $pid | awk 'NR>1')
  if [[ -n "$process_info" ]]; then
      status="running"
      mem_used=$(echo "$process_info" | awk '{print $1/1024 "MB"}')
      cpu_usage=$(echo "$process_info" | awk '{print $2"%"}')
  else
      status="killed"
  fi

  echo "Status: $status"
  echo "Memory used: $mem_used"
  echo "CPU usage: $cpu_usage"

  # Count file descriptors for the process
  file_descriptors=$(ls /proc/$pid/fd/ 2>/dev/null | wc -l)
  echo "File descriptors: $file_descriptors"

  # Check if a "record_store" directory exists and display information if found
  record_store_dir="$base_dir/$dir/record_store"
  if [ -d "$record_store_dir" ]; then
    records=$(ls -1 $record_store_dir | wc -l)
    echo "Records: $records"

    disk_usage=$(du -sh "$record_store_dir" | awk '{print $1}' | sed 's/M/MB/')
    echo "Disk usage: $disk_usage"
  else
    echo "$dir does not contain record_store"
  fi

  # Retrieve rewards balance using the 'safe wallet balance' command
  rewards_balance=$(${HOME}/.local/bin/safe wallet balance --peer-id="$dir" | grep -oP '(?<=: )\d+\.\d+')
  echo "Rewards balance: $rewards_balance"

  echo
  node_number=$((node_number + 1))
done

echo "------------------------------------------"
