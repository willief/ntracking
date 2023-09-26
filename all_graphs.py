import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import os
import glob
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

user_home = os.path.expanduser("~")
datadir = os.path.join(user_home, ".local", "share", "safe", "tools", "rewards_plotting")


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


def combined_extract_data(filenames):
    all_data = []

    # This part is common for both requirements
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
            else:
                idx += 1

        all_data.extend(data)

    # DataFrame for rewards_visualize and memory_visualize
    line_df = pd.DataFrame(all_data)
    line_df["Timestamp"] = pd.to_datetime(line_df["Global (UTC) Timestamp"], format='%a %b %d %H:%M:%S %Z %Y', errors='coerce')
    if line_df["Timestamp"].dt.tz is None:
        line_df["Timestamp"] = line_df["Timestamp"].dt.tz_localize('UTC')

    # DataFrame for logarithmic_bubble_visualize
    bubble_df = line_df.copy().dropna(subset=["Timestamp"])
    bubble_df = bubble_df.groupby("Node").last().reset_index()

    return line_df, bubble_df

def generate_pid_to_color(pids):
    colormap = plt.cm.tab20c
    pid_colors = [colormap(i % 20) for i in range(len(pids))]
    pid_colors_str = ["rgb({:.0f}, {:.0f}, {:.0f})".format(r*255, g*255, b*255) for r, g, b, _ in pid_colors]
    return {pid: pid_colors_str[i] for i, pid in enumerate(pids)}

# Visualization
custom_hovertemplate = "%{customdata[0]}<br>" + \
                       "Records: %{customdata[1]}<br>" + \
                       "Disk usage: %{customdata[2]}MB<br>" + \
                       "Memory used: %{customdata[3]:.2f}MB<br>" + \
                       "CPU usage: %{customdata[4]:.2f}%<br>" + \
                       "File descriptors: %{customdata[5]}<br>"

def rewards_visualize(df):
    pid_to_color = generate_pid_to_color(sorted(df['PID'].unique()))
    fig = px.line(df, x="Timestamp", y="Rewards balance", color="PID", line_group="PID",
        custom_data=["Number", "Records", "Disk usage", "Memory used", "CPU usage", 
                               "File descriptors", "Rewards balance"],
        labels={"Rewards balance": "Rewards Balance"},
        color_discrete_map=pid_to_color)

    # Hide the x-axis labels (Timestamp)
    fig.update_layout(
        xaxis_title_text="Rewards Over Time",
        yaxis_title_text=""
    )


    for trace in fig.data:
        trace.hovertemplate = custom_hovertemplate

    fig.update_layout(
        hovermode='y unified',
        paper_bgcolor='#252526',
        plot_bgcolor='#070D0D',
        margin=dict(t=32, b=32, l=32, r=32, pad=2),
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=3, label="3 hours", step="hour", stepmode="backward"),
                    dict(count=6, label="6 hours", step="hour", stepmode="backward"),
                    dict(count=12, label="12 hours", step="hour", stepmode="backward"),
                    dict(count=1, label="24 hours", step="day", stepmode="backward"),
                    dict(count=3, label="3 days", step="day", stepmode="backward"),
                    dict(count=7, label="Week", step="day", stepmode="backward"),
                    #dict(count=30, label="30 days", step="day", stepmode="backward"),
                    #dict(count=3, label="3 months", step="month", stepmode="backward"),
                    #dict(count=6, label="6 months", step="month", stepmode="backward"),
                    dict(step="all", label="All Data")
                ],
                font=dict(color="#ffffff"),  # Changing the color of the range selector text
                bgcolor='#424241'
            ),
            type="date",
            showgrid=True, 
            gridcolor='#171515', 
            gridwidth=0.01
        ),                
        yaxis=dict(showgrid=True, gridcolor='#171515', gridwidth=0.01),
        font=dict(color='#ffffff')
    )                      

    # Specify the path and save the figure
    output_html_path = os.path.join(datadir, "rewards_balance_plot.html")
    fig.write_html(output_html_path)

def memory_visualize(df):
    pid_to_color = generate_pid_to_color(sorted(df['PID'].unique()))
    fig = px.line(df, x="Timestamp", y="Memory used", color="PID", line_group="PID",
        custom_data=["Number", "Records", "Disk usage", "Memory used", "CPU usage", 
                               "File descriptors", "Rewards balance"],
        labels={"Memory": "Memory Usage (MB)"},
        color_discrete_map=pid_to_color)


    # Hide the x-axis labels (Timestamp)
    fig.update_layout(
        xaxis_title_text="Memory Over Time",
        yaxis_title_text=""
    )
    for trace in fig.data:
        trace.hovertemplate = custom_hovertemplate

    fig.update_layout(
        hovermode='y unified',
        paper_bgcolor='#252526',
        plot_bgcolor='#070D0D',
        margin=dict(t=32, b=32, l=32, r=32, pad=2),
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=3, label="3 hours", step="hour", stepmode="backward"),
                    dict(count=6, label=" 6 hours", step="hour", stepmode="backward"),
                    dict(count=12, label=" 12 hours", step="hour", stepmode="backward"),
                    dict(count=1, label=" 24 hours", step="day", stepmode="backward"),
                    dict(count=3, label=" 3 days", step="day", stepmode="backward"),
                    dict(count=7, label=" Week", step="day", stepmode="backward"),
                    dict(step="all", label="All Data")
                ],
                font=dict(color="#ffffff"),  # Changing the color of the range selector text
                bgcolor='#424241'
            ),
            type="date",
            showgrid=True, 
            gridcolor='#171515', 
            gridwidth=0.01
        ),                
        yaxis=dict(showgrid=True, gridcolor='#171515', gridwidth=0.01),
        font=dict(color='#ffffff')
    )  

    # Specify the path and save the figure
    output_html_path = os.path.join(datadir, "memory_usage_plot.html")
    fig.write_html(output_html_path) 

def logarithmic_bubble_visualize(df):
    df["x"] = np.random.rand(len(df))
    df["y"] = np.random.rand(len(df))
    df["log_rewards"] = 2 * np.log(df["Rewards balance"] + 1)
    
    pid_to_color = generate_pid_to_color(sorted(df['PID'].unique()))

    fig = px.scatter(df, x="x", y="y", size="log_rewards", color="PID", hover_name="Node",
                 hover_data=["Number", "Node", "PID", "Rewards balance", "Records"],
                 labels={"log_rewards": "Rewards Balance"},
                 color_discrete_map=pid_to_color,
                 size_max=100)
    
    fig.update_traces(
        hovertemplate="Number: %{customdata[0]}<br>Node: %{customdata[1]}<br>PID: %{customdata[2]}<br>Rewards balance: %{customdata[3]:.9f}<br>Records: %{customdata[4]}<extra></extra>",  # Added Records here
        marker=dict(line=dict(width=0.5, color='#252526')),  # this makes the hover border color consistent
        selector=dict(mode='markers+text')
    )
    
    fig.update_layout(
        hovermode='closest',
        paper_bgcolor='#252526',
        plot_bgcolor='#070D0D',
        margin=dict(t=32, b=32, l=32, r=32, pad=2),
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=False),
        legend_title_font_color='#ffffff',
        legend_font_color='#ffffff',
        hoverlabel=dict(bgcolor='#252526', font_color='#ffffff'),  # consistent hover box color
        showlegend=False  # Hides the legend
    )
    
    # Remove x and y from hover labels
    # Remove x and y from hover labels
    fig.update_traces(hovertemplate="Number: %{customdata[0]}<br>Node: %{customdata[1]}<br>Rewards balance: %{customdata[3]:.9f}<br>Records: %{customdata[4]}<extra></extra>")

    # Specify the path and save the figure
    output_html_path = os.path.join(datadir, "bubble_rewards.html")
    fig.write_html(output_html_path) 
# Scanning for log files in 'datadir'
log_files = glob.glob(os.path.join(datadir, "resources*.log"))

if not log_files:
    print("No log files found!")
    exit()

if __name__ == "__main__":
    line_df, bubble_df = combined_extract_data(log_files)
    rewards_visualize(line_df)
    memory_visualize(line_df)
    logarithmic_bubble_visualize(bubble_df)