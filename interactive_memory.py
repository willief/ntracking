import pandas as pd
import plotly.express as px
import os
import warnings warnings.simplefilter(action='ignore', category=FutureWarning)

user_home = os.path.expanduser("~")
datadir = os.path.join(user_home, ".local", "share", "safe", "tools", "rewards_plotting")

def detect_log_files(directory="."):
    """Detect and return a list of available log files in the specified directory."""
    log_files = []
    
    # Check if 'resources.log' exists
    if os.path.exists(os.path.join(directory, "resources.log")):
        log_files.append("resources.log")
    
    # Check for subsequent log files (resources1.log, resources2.log, ...)
    i = 1
    while True:
        log_file_name = f"resources{i}.log"
        if os.path.exists(os.path.join(directory, log_file_name)):
            log_files.append(log_file_name)
            i += 1
        else:
            break

    return log_files


def convert_value(value, format_type, default=0):
    if format_type == 'float':
        try:
            return float(value)
        except ValueError:
            return default
    elif format_type == 'int':
        try:
            return int(value)
        except ValueError:
            return default
    elif format_type == 'float_mb':
        try:
            return float(value.replace("MB", "").strip())
        except ValueError:
            return default
    elif format_type == 'float_percent':
        try:
            return float(value.replace("%", "").strip())
        except ValueError:
            return default
    return value

def enhanced_extract_data(filenames):
    all_data = []
    
    # Iterate over each file and extract data
    for file_number, filename in enumerate(filenames):
        with open(filename, "r") as file:
            lines = file.readlines()

        formats = {
            "Memory used": "float_mb",
            "Records": "int",
            "Disk usage": "float_mb",
            "CPU usage": "float_percent",
            "File descriptors": "int",
            "Rewards balance": "float"
        }

        data = []
        idx = 0
        while idx < len(lines):
            if "Global (UTC) Timestamp:" in lines[idx]:
                timestamp = lines[idx].split(": ", 1)[1].strip()
                entry_data = {"Global (UTC) Timestamp": timestamp}
                
                idx += 1
                while idx < len(lines) and "------------------------------------------" not in lines[idx]:
                    if ": " in lines[idx]:
                        key, raw_value = lines[idx].split(": ", 1)
                        if key in formats:
                            value = convert_value(raw_value, formats[key])
                        else:
                            value = raw_value.strip()
                        
                        if key == "Number":
                            entry_data[key] = f"{file_number + 1}:{value}"
                        else:
                            entry_data[key] = value
                    idx += 1
                
                required_keys = ["Global (UTC) Timestamp", "Node", "PID", "Memory used", "Records", 
                                 "Disk usage", "CPU usage", "File descriptors", "Rewards balance"]
                if all(k in entry_data for k in required_keys):
                    data.append([
                        timestamp, 
                        entry_data["Node"], 
                        entry_data["Number"],
                        entry_data["PID"], 
                        entry_data["Memory used"], 
                        entry_data["Records"],
                        entry_data["Disk usage"], 
                        entry_data["CPU usage"], 
                        entry_data["File descriptors"], 
                        entry_data["Rewards balance"]
                    ])
            else:
                idx += 1

        all_data.extend(data)

    df = pd.DataFrame(all_data, columns=["Timestamp", "Node", "Number", "PID", "Memory", "Records", 
                                        "Disk usage", "CPU usage", "File descriptors", "Rewards balance"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format='%a %b %d %H:%M:%S %Z %Y', errors='coerce')
    if df["Timestamp"].dt.tz is None:
        df["Timestamp"] = df["Timestamp"].dt.tz_localize('UTC')
    return df


# Visualization
custom_hovertemplate = "%{customdata[0]}<br>" + \
                       "Records: %{customdata[1]}<br>" + \
                       "Disk usage: %{customdata[2]}MB<br>" + \
                       "Memory used: %{customdata[3]:.2f}MB<br>" + \
                       "CPU usage: %{customdata[4]:.2f}%<br>" + \
                       "File descriptors: %{customdata[5]}<br>"
                       
                       
def visualize(df):
    fig = px.line(df, x="Timestamp", y="Memory", color="PID", line_group="PID",
                  custom_data=["Number", "Records", "Disk usage", "Memory", "CPU usage", 
                               "File descriptors", "Rewards balance"],
                  labels={"Memory": "Memory Usage (MB)"})

    for trace in fig.data:
        trace.hovertemplate = custom_hovertemplate

    fig.update_layout(
        hovermode='y unified',
        paper_bgcolor='#252526',
        plot_bgcolor='#070D0D',
        margin=dict(t=42, b=42, l=42, r=42, pad=2),
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="Today", step="day", stepmode="todate"),
                    dict(count=1, label="Last 24 hours", step="day", stepmode="backward"),
                    dict(count=3, label="Last 3 days", step="day", stepmode="backward"),
                    dict(count=7, label="Last Week", step="day", stepmode="backward"),
                    dict(step="all", label="All Data")
                ],
                font=dict(color="#993d00")  # Dark color for range selector text
            ),
            type="date",
            showgrid=True, 
            gridcolor='#252526', 
            gridwidth=0.01
        ),                
        yaxis=dict(showgrid=True, gridcolor='#252526', gridwidth=0.01),
        font=dict(color='#ffffff')
    )
    
# Output
    output_html_path = "output_html_path"
    fig.write_html(output_html_path)


file_list = ["datadir + "/resources1.log", "datadir + "/resources2.log", "datadir + "/resources3.log"]
output_html_file = 'memory_usage_plot.html'
df = enhanced_extract_data(detect_log_files("/mnt/data"))
output_html_path = os.path.join(datadir, output_html_file)
visualize(df)
