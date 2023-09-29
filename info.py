
import re
from datetime import datetime, timedelta
import glob

def parse_log(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    entries = content.split('------------------------------------------')
    
    # Required fields
    number_pattern = r"Number: (\d+)"
    node_pattern = r"Node: ([\w\d]+)"
    pid_pattern = r"PID: (\d+)"
    reward_pattern = r"Rewards balance: ([\d.]+)"
    timestamp_pattern = r"Global \(UTC\) Timestamp: (.+?)\n"
    status_pattern = r"Status: (\w+)"

    parsed_entries = []
    dead_nodes = []  # List to store nodes with issues
    first_killed_info = None  # Placeholder for the first killed info
    
    for entry in entries:
        number_match = re.search(number_pattern, entry)
        node_match = re.search(node_pattern, entry)
        pid_match = re.search(pid_pattern, entry)
        reward_match = re.search(reward_pattern, entry)
        timestamp_match = re.search(timestamp_pattern, entry)
        status_match = re.search(status_pattern, entry)
        
        if all([number_match, node_match, pid_match, reward_match, timestamp_match, status_match]):
            timestamp = datetime.strptime(timestamp_match.group(1), '%a %b %d %H:%M:%S UTC %Y')
            parsed_entry = {
                'Number': int(number_match.group(1)),
                'Node': node_match.group(1),
                'PID': int(pid_match.group(1)),
                'Reward': float(reward_match.group(1)),
                'Timestamp': timestamp,
                'Status': status_match.group(1)
            }
            parsed_entries.append(parsed_entry)
            
            identifier = (parsed_entry['Number'], parsed_entry['Node'], parsed_entry['PID'])
            
            # Check if node has a dead status and hasn't been added to dead_nodes
            if parsed_entry['Status'] != 'running' and identifier not in [(x['Number'], x['Node'], x['PID']) for x in dead_nodes]:
                dead_nodes.append(parsed_entry)
                if first_killed_info is None:
                    first_killed_info = parsed_entry
    
    return parsed_entries, dead_nodes, first_killed_info

def main():
    all_entries = []
    all_dead_nodes = []
    all_first_killed_info = None
    
    for file_path in glob.glob("resources*.log"):
        entries, dead_nodes, first_killed_info = parse_log(file_path)
        all_entries.extend(entries)
        all_dead_nodes.extend(dead_nodes)
        if first_killed_info:
            all_first_killed_info = first_killed_info
    
    unique_entries = {}
    for entry in all_entries:
        key = (entry['Number'], entry['Node'], entry['PID'])
        if key not in unique_entries or unique_entries[key]['Timestamp'] < entry['Timestamp']:
            unique_entries[key] = entry

    sorted_entries = sorted(unique_entries.values(), key=lambda x: x['Reward'], reverse=True)
    total_reward = sum([entry['Reward'] for entry in unique_entries.values()])
    
    # Counting unique running and killed nodes
    running_nodes = set(entry['Node'] for entry in unique_entries.values() if entry['Status'] == 'running')
    killed_nodes = set(entry['Node'] for entry in unique_entries.values() if entry['Status'] == 'killed')
    
    with open("sorted_results.txt", "w") as outfile:
        outfile.write("=== Node Info ===\n\n")
        outfile.write(f"Total Rewards: {total_reward:.8f}\n\n")
        outfile.write(f"Running Nodes: {len(running_nodes)}\n\n")
        outfile.write(f"Dead Nodes: {len(killed_nodes)}\n\n")
        
        if all_dead_nodes:
            outfile.write("=== Dead Nodes Details ===\n")
            for node in all_dead_nodes:
                outfile.write(f"Number: {node['Number']}\n")
                outfile.write(f"Node: {node['Node']}\n")
                outfile.write(f"PID: {node['PID']}\n")
                outfile.write(f"Status: {node['Status']}\n")
                outfile.write(f"Total Rewards: {total_reward:.8f}\n")

                if all_first_killed_info and (node['Number'] == all_first_killed_info['Number']):
                    first_killed_time = all_first_killed_info['Timestamp'].strftime('%a %b %d %H:%M:%S UTC %Y')
                    first_killed_reward = all_first_killed_info['Reward']
                    outfile.write(f"First Killed At: {first_killed_time}\n")
                    outfile.write(f"Rewards Balance When Killed: {first_killed_reward:.8f}\n")

            outfile.write("---------\n\n")
    
        outfile.write("=== Best Earners Decending ===\n")
        
        for entry in sorted_entries:
            outfile.write(f"Number: {entry['Number']}\n")
            outfile.write(f"Node: {entry['Node']}\n")
            outfile.write(f"PID: {entry['PID']}\n")
            outfile.write(f"Rewards balance: {entry['Reward']:.8f}\n")
            outfile.write("---------\n")

if __name__ == "__main__":
    main()
