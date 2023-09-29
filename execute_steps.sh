
#!/bin/bash

# Navigate to the directory
cd /home/josh/.local/share/safe/tools/rewards_plotting/

# Execute the rewards_logs.sh script
/home/josh/.local/share/safe/tools/rewards_plotting/rewards_logs.sh

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Get Node Info
python3 info.py

# Generate the graphs
python3 all_graphs.py

# Deactivate the virtual environment (optional but recommended)
deactivate

# Navigate to the javages.github.io directory
cd ~/safeplots_all/javages.github.io

# Copy the file
cp /home/josh/.local/share/safe/tools/rewards_plotting/rewards_balance_plot.html .
cp /home/josh/.local/share/safe/tools/rewards_plotting/bubble_rewards.html .
cp /home/josh/.local/share/safe/tools/rewards_plotting/memory_usage_plot.html .
cp /home/josh/.local/share/safe/tools/rewards_plotting/durations.html .
cp /home/josh/.local/share/safe/tools/rewards_plotting/sorted_results.txt .

# Commit and push the changes
git add rewards_balance_plot.html memory_usage_plot.html bubble_rewards.html durations.html sorted_results.txt
git commit -m "Auto Update"
git push origin main

