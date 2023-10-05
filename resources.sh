#!/bin/bash

base_dir="${HOME}/.local/share/safe/node"
declare -A dir_pid
node_number=0

for dir in "$base_dir"/*; do
  if [[ -f "$dir/safenode.pid" ]]; then
    dir_name=$(basename "$dir")
    dir_pid["$dir_name"]=$(cat "$dir/safenode.pid")
  fi
done

for dir in "${!dir_pid[@]}"; do
  pid=${dir_pid[$dir]}

  echo "------------------------------------------"
  echo "Local Timestamp: $(date +'%a %b %d %H:%M:%S %Z %Y')"
  echo "Global (UTC) Timestamp: $(TZ='UTC' date +'%a %b %d %H:%M:%S %Z %Y')"
  echo "Number: $node_number"
  echo "Node: $dir"
  echo "PID: $pid"

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

  #file_descriptors=$(ls /proc/$pid/fd/ 2>/dev/null | wc -l)
  #echo "File descriptors: $file_descriptors"
  
  tcp_established=$(lsof -n -iTCP -a -p $pid 2>/dev/null | grep "ESTABLISHED" | wc -l)
  echo "TCP connections (established): $tcp_established"

  record_store_dir="$base_dir/$dir/record_store"
  if [ -d "$record_store_dir" ]; then
    records=$(ls -1 $record_store_dir | wc -l)
    echo "Records: $records"

    disk_usage=$(du -sh "$record_store_dir" | awk '{print $1}' | sed 's/M/MB/')
    echo "Disk usage: $disk_usage"
  else
    echo "$dir does not contain record_store"
  fi

  rewards_balance=$(${HOME}/.local/bin/safe wallet balance --peer-id="$dir" | grep -oP '(?<=: )\d+\.\d+')
  echo "Rewards balance: $rewards_balance"

  echo
  node_number=$((node_number + 1))
done

echo "------------------------------------------"
