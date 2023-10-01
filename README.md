# SN Nodes Stats & Tracking 
See https://javages.github.io

Track Safe Network nodes.

## Requirements

- recent Linux. preferably Ubuntu
- safe client
- safe node
- sudo access - (ONLY if venv is not already installed)

## Setup

- Ensure the script is executable:

  ```bash
  chmod +x path_to_script/setup.sh

  ```

- Execute the script

 ```bash
  ./path_to_script/setup.sh

  ```

> **Note**: This script will install a virtual environment using venv. This helps to avoid potential conflicts between packages and ensures a clean, isolated environment for your project. If venv is not on your system already, you will be prompted for your password to continue.

### 1. Script Placement & Permissions

This script will install to $(HOME)/.local/share/safe/tools/Rewards_plotting; modify as needed.
All necessary permissions and crontab entries are now set by the script.

### 2. Cron Job Setup

- The setup script will add the following entry to your crontab with the option to add a second to also automate graph creation.

```bash
  */10 * * * * /bin/bash $(HOME)/.local/share/safe/tools/Rewards_plotting/resources.sh >> $(HOME)/.local/share/safe/tools/Rewards_plotting/resources.log 2>&1
  ```
  
This job will take a snapshot of your node/nodes resources and rewards balance every 10 minutes. The data will be appended to `resources.log`.

- To change this interval or data destination, open the crontab for editing:

  ```bash
  crontab -e

  Note: Don't forget to comment out or remove this cron job if you no longer need it (in between tests), as it will run indefinitely otherwise.
  Also remember to remove the resources.log file between runs!  ##TODO   cleanup script

### 3. Graph Generation

- Once you have run for a few hours and have enough data, you can generate the graph.
- Execute the script:

  ```bash
  ./create_graphs.sh
  ```

### 4. View the Graphs SN-StatsNTracking.html

- The resulting plots will be saved in the app directory at
`~/.local/share/safe/tools/SN-StatsNTracking/`.
- The graphs are interactive: you can zoom in, select specific nodes, and more using most browsers.

For all functionality of SN-StatsNTracking.html to work locally you will need to:
`cd .local/share/safe/tools/SN-StatsNTracking`
`source /RPvenv/bin/activate`
`python -m http.server`
Open your browser and navigate to 
`http://localhost:8000`
Open `SN-StatsNTracking.html` from list of displayed files.
This can be left open, it will refresh/update periodically if you chose to auto generate graphs. 

To end the session return to your terminal and `Ctrl + C`

