#!/bin/bash

install_dir="${HOME}/.local/share/safe/tools/ntracking

cd $install_dir

# Activate virtual environment
source $install_dir/RPvenv/bin/activate

python3 ./all_graphs.py

sleep 1
python3 ./info.py


