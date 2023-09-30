#!/bin/bash

install_dir="${HOME}/.local/share/safe/tools/SN-StatsNTracking

cd $install_dir

# Activate virtual environment
source $install_dir/venv/bin/activate

python3 ./all_graphs.py

sleep 1
python3 ./info.py


