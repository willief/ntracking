#!/bin/bash

registry_file="node_registry.conf"
base_dir="${HOME}/.local/share/safe/node"

declare -A dir_pid
declare -A node_numbers
declare -A dir_creation_times

# Ensure the registry file exists with correct permissions
if [[ ! -f $registry_file ]]; then
    touch "$registry_file"
    chmod 644 "$registry_file"
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to set permissions on $registry_file. Check your user permissions."
        exit 1
    fi
fi

# Load node numbers from the registry
while IFS=: read -r node_name number; do
    node_numbers["$node_name"]=$number
done < "$registry_file"

# Identify the highest node number in the registry
max_number=-1
for number in "${node_numbers[@]}"; do
  ((number > max_number)) && max_number=$number
done

# Discover nodes and capture their details
for dir in "$base_dir"/*; do
  if [[ -f "$dir/safenode.pid" ]]; then
    dir_name=$(basename "$dir")
    dir_pid["$dir_name"]=$(cat "$dir/safenode.pid")
    dir_creation_times["$dir_name"]=$(stat -c %W "$dir")  # Capture creation time

    # Assign a new number to unregistered nodes
    [[ -z ${node_numbers["$dir_name"]} ]] && node_numbers["$dir_name"]=$((++max_number))
  fi
done

# Sort nodes by creation time and log their details
readarray -t sorted_dirs < <(for dir_name in "${!node_numbers[@]}"; do printf "%s:%s\n" "${node_numbers[$dir_name]}" "$dir_name"; done | sort -n | cut -d: -f2)
for dir_name in "${sorted_dirs[@]}"; do
  echo "------------------------------------------"
  echo "Global (UTC) Timestamp: $(TZ='UTC' date +'%a %b %d %H:%M:%S %Z %Y')"
  echo "Number: ${node_numbers[$dir_name]}"
  echo "Node: $dir_name"
  echo "PID: ${dir_pid[$dir_name]}"

  # Retrieve process information
  process_info=$(ps -o rss,%cpu -p "${dir_pid[$dir_name]}" | awk 'NR>1')
  if [[ -n $process_info ]]; then
      echo "Status: running"
      echo "Memory used: $(awk '{print $1/1024 "MB"}' <<< "$process_info")"
      echo "CPU usage: $(awk '{print $2"%"}' <<< "$process_info")"
  else
      echo "Status: killed"
  fi

  # Count established TCP connections
  tcp_established=$(lsof -n -iTCP -a -p "${dir_pid[$dir_name]}" 2>/dev/null | grep -c "ESTABLISHED")
  echo "TCP connections (established): $tcp_established"

  # Check for record store and report its details
  record_store_dir="$base_dir/$dir_name/record_store"
  if [[ -d "$record_store_dir" ]]; then
    records=$(find "$record_store_dir" -type f | wc -l)
    echo "Records: $records"
    echo "Disk usage: $(du -sh "$record_store_dir" | cut -f1)"
  else
    echo "$dir_name does not contain record_store"
  fi

  # Retrieve and display rewards balance
  rewards_balance=$(${HOME}/.local/bin/safe wallet balance --peer-id="$dir_name" | grep -oP '(?<=: )\d+\.\d+')
  echo "Rewards balance: $rewards_balance"

  echo
done

# Update the registry file if new nodes were added
{
  for node_name in "${!node_numbers[@]}"; do
    echo "$node_name:${node_numbers[$node_name]}"
  done
} > "$registry_file"

echo "------------------------------------------"

