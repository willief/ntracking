#!/bin/bash

install_dir="${HOME}/ntracking"

cd $install_dir

# Activate virtual environment
source $install_dir/venv/bin/activate

python3 ./all_graphs.py

sleep 1
python3 ./node_info.py


