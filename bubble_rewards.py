import pandas as pd
import numpy as np
import os
import plotly.express as px
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
    for file_number, filename in enumerate(filenames):
        with open(filename, "r") as file:
            lines = file.readlines()
        formats = {
            "Memory used": "float_mb",
            "Records": "int",
            "Disk usage": "float_mb",
            "CPU usage": "float_percent",
            "File descriptors": "int",
            "Rewards balance": "float",
            "Number": "int"
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
                data.append(entry_data)
            idx += 1
        all_data.extend(data)
    df = pd.DataFrame(all_data)
    df = df.dropna(subset=["Global (UTC) Timestamp"])
    df["Timestamp"] = pd.to_datetime(df["Global (UTC) Timestamp"], errors='coerce')
    df = df.dropna(subset=["Timestamp"]).groupby("Node").last().reset_index()
    return df

def logarithmic_bubble_visualize(df):
    df["x"] = np.random.rand(len(df))
    df["y"] = np.random.rand(len(df))
    df["log_rewards"] = 2 * np.log(df["Rewards balance"] + 1)
    
    fig = px.scatter(df, x="x", y="y", size="log_rewards", color="PID", hover_name="Node",
                     hover_data=["Number", "Node", "PID", "Rewards balance"], 
                     labels={"log_rewards": "Rewards Balance"},
                     size_max=100)
    
    fig.update_traces(
        hovertemplate="Number: %{customdata[0]}<br>Node: %{customdata[1]}<br>PID: %{customdata[2]}<br>Rewards balance: %{customdata[3]:.9f}<extra></extra>",
        marker=dict(line=dict(width=0.5, color='#252526')), # this makes the hover border color consistent
        selector=dict(mode='markers+text')
    )
    
    fig.update_layout(
        hovermode='closest',
        paper_bgcolor='#252526',
        plot_bgcolor='#070D0D',
        margin=dict(t=42, b=42, l=42, r=42, pad=2),
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=False),
        legend_title_font_color='#ffffff',
        legend_font_color='#ffffff',
        hoverlabel=dict(bgcolor='#252526', font_color='#ffffff') # consistent hover box color
    )
    
    # Remove x and y from hover labels
    fig.update_traces(hovertemplate="Number: %{customdata[0]}<br>Node: %{customdata[1]}<br>PID: %{customdata[2]}<br>Rewards balance: %{customdata[3]:.9f}<extra></extra>")


# Output
    output_html_path = "output_html_path"
    fig.write_html(output_html_path)
    return output_html_path

output_html_file = 'rewards_balance_plot.html'
file_list = ["datadir + "/resources1.log", "datadir + "/resources2.log", "datadir + "/resources3.log"]
output_html_path = os.path.join(datadir, output_html_file)
df = enhanced_extract_data(detect_log_files("/mnt/data"))
log_bubble_plot_path = logarithmic_bubble_visualize(df)
