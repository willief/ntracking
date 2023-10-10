#!/bin/bash

#!${HOME}/ntracking/RPvenv/bin/python

# Display the version of pip
pip --version

# Install the 'pandas' and 'plotly.express' Python packages using pip3
echo "installing pandas"
pip3 install pandas

echo "installing plotly"
pip3 install plotly.express

echo "installing matplotlib"
pip3 install matplotlib
echo ""
echo ""
echo "All required packages have been installed"
echo ""
echo "--------------------------------------------"
