#!/bin/bash

install_dir="${HOME}/.local/share/safe/tools/rewards_plotting"

cd $install_dir

#Activate virtual environment
source $install_dir/RPvenv/bin/activate

python3 ./interactive_rewards.py
python3 ./interactive_memory.py
python3 ./bubble_rewards.py
