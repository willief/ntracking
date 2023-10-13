import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import glob
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

user_home = os.path.expanduser("~")
datadir = os.path.join(user_home, "wyse_graphs")

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

from datetime import datetime, timedelta

def selective_data(data):
    now = datetime.now()
    limit_24h = now - timedelta(hours=24)
    limit_48h = now - timedelta(hours=48)
    limit_72h = now - timedelta(hours=72)
    limit_120h = now - timedelta(hours=120)

    refined_data = []

    for record in data:
        timestamp_str = record['Global (UTC) Timestamp']
        timestamp = datetime.strptime(timestamp_str, '%a %b %d %H:%M:%S %Z %Y')

        time_diff = now - timestamp
        hours_diff = time_diff.total_seconds() / 3600

        if hours_diff <= 24:
            interval = 0  # keep all
        elif hours_diff <= 48:
            interval = 15  # every 15 minutes
        elif hours_diff <= 72:
            interval = 30  # every 30 minutes
        elif hours_diff <= 120:
            interval = 60  # every hour
        else:
            interval = 240  # every 4 hours

        if interval == 0 or (timestamp.minute == 0 and timestamp.hour % (interval // 60) == 0):
            refined_data.append(record)

    return refined_data


def combined_extract_data(filenames):
    filenames = sorted(filenames)
    all_data = []

    for file_number, filename in enumerate(filenames):
        with open(filename, "r") as file:
            lines = file.readlines()

        formats = {
            "Memory used": "float_mb",
            "Records": "int",
            "Disk usage": "float_mb",
            "TCP connections (established)": "int",
            "Rewards balance": "float",
            "Number": "int",
            "PID": "int"
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

                        if key == "PID":
                            entry_data[key] = int(raw_value.strip())

                    idx += 1
                data.append(entry_data)
            else:
                idx += 1

        all_data.extend(data)
    
    filtered_data = selective_data(all_data)

    # DataFrame for rewards_visualize and memory_visualize
    line_df = pd.DataFrame(filtered_data)
    line_df["Timestamp"] = pd.to_datetime(line_df["Global (UTC) Timestamp"], format='%a %b %d %H:%M:%S %Z %Y', errors='coerce')
    if line_df["Timestamp"].dt.tz is None:
        line_df["Timestamp"] = line_df["Timestamp"].dt.tz_localize('UTC')

    # DataFrame for logarithmic_bubble_visualize
    bubble_df = line_df.copy().dropna(subset=["Timestamp"])
    bubble_df = bubble_df.groupby("Node").last().reset_index()

    return line_df, bubble_df

def generate_Number_to_color(Number):
    colormap = plt.cm.tab20c
    Number_colors = [colormap(i % 20) for i in range(len(Number))]
    Number_colors_str = ["rgb({:.0f}, {:.0f}, {:.0f})".format(r*255, g*255, b*255) for r, g, b, _ in Number_colors]
    return {Number: Number_colors_str[i] for i, Number in enumerate(Number)}

# Visualization
custom_hovertemplate = "%{customdata[3]}<br>"

def rewards_visualize(df):
    Number_to_color = generate_Number_to_color(sorted(df['Number'].unique()))
    fig = px.line(df, x="Timestamp", y="Rewards balance", color="Number", line_group="Number",
        custom_data=["Number", "Rewards balance", "Node", "PID"],
        labels={"Rewards balance": "Rewards Balance"},
        color_discrete_map=Number_to_color)

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
                    dict(step="all", label="All Data")
                ],
                font=dict(color="#ffffff"),
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

    output_html_path = os.path.join(datadir, "rewards_balance_plot.html")
    fig.write_html(output_html_path)

def memory_visualize(df):
    Number_to_color = generate_Number_to_color(sorted(df['Number'].unique()))
    fig = px.line(df, x="Timestamp", y="Memory used", color="Number", line_group="Number",
        custom_data=["Number", "Memory used", "Node", "PID"],
        labels={"Memory": "Memory Usage (MB)"},
        color_discrete_map=Number_to_color)


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
                font=dict(color="#ffffff"),
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

    output_html_path = os.path.join(datadir, "memory_usage_plot.html")
    fig.write_html(output_html_path) 

def tcp_visualize(df):
    Number_to_color = generate_Number_to_color(sorted(df['Number'].unique()))
    fig = px.line(df, x="Timestamp", y="TCP connections (established)", color="Number", line_group="Number",
        custom_data=["Number", "PID"],
        labels={"Memory": "Memory Usage (MB)"},
        color_discrete_map=Number_to_color)

    # Define a custom hovertemplate
    hover_template = "%{customdata[1]}"

    # Apply the custom hovertemplate to all traces
    for trace in fig.data:
        trace.hovertemplate = hover_template

    # Hide the x-axis labels (Timestamp)
    fig.update_layout(
        xaxis_title_text="TCP connections (established)",
        yaxis_title_text=""
    )

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
                font=dict(color="#ffffff"),
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

    output_html_path = os.path.join(datadir, "tcp.html")
    fig.write_html(output_html_path)    

def logarithmic_bubble_visualize(df):
    df["x"] = np.random.rand(len(df))
    df["y"] = np.random.rand(len(df))
    df["log_rewards"] = 2 * np.log(df["Rewards balance"] + 1)
    
    Number_to_color = generate_Number_to_color(sorted(df['Number'].unique()))

    fig = px.scatter(df, x="x", y="y", size="log_rewards", color="Number", hover_name="Node",
                 hover_data=["Number", "Rewards balance"],
                 labels={"log_rewards": "Rewards Balance"},
                 color_discrete_map=Number_to_color,
                 size_max=100)
    
    fig.update_traces(
        hovertemplate="Number: %{customdata[0]}<br>Rewards balance: %{customdata[1]:.9f}<extra></extra>",
        marker=dict(line=dict(width=0.5, color='#252526')),
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
        hoverlabel=dict(bgcolor='#252526', font_color='#ffffff'),
        showlegend=False
    )
    
    # Remove x and y from hover labels
    # Remove x and y from hover labels
    fig.update_traces(hovertemplate="Number: %{customdata[0]}<br>Rewards balance: %{customdata[1]:.9f}<extra></extra>")

    output_html_path = os.path.join(datadir, "bubble_rewards.html")
    fig.write_html(output_html_path) 

log_files = glob.glob(os.path.join(datadir, "resources*.log"))


def records_visualize(df):
    if 'Number' in df.columns and df['Number'].str.contains(':').all():
        df[['log_number', 'node_number']] = df['Number'].str.split(':', expand=True).astype(int)
        df = df.sort_values(['log_number', 'node_number'], ascending=[True, True])
        df = df.drop(['log_number', 'node_number'], axis=1)

    else:
        raise ValueError("Column 'Number' is missing or not in the expected format 'log_number:node_number'")

    df['Record Count'] = df['Records']

    # Remove duplicates, keeping the last entry per 'Number'
    df = df.drop_duplicates(subset='Number', keep='last')

    # Generate colors
    Number_to_color = generate_Number_to_color(sorted(df['Number'].unique()))

    # Create the bar plot
    fig = px.bar(
        df, 
        x="Number", 
        y="Record Count",
        color="Number",
        labels={"Record Count": "Record Count"},
        color_discrete_map=Number_to_color,
        opacity=1.0
    )
    
    # Update layout settings
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='#252526',
        plot_bgcolor='#070D0D',
        margin=dict(t=32, b=32, l=32, r=32, pad=2),             
        yaxis=dict(
            showgrid=True, 
            gridcolor='#171515', 
            gridwidth=0.01,
        ),
        font=dict(color='#ffffff')
    )
    
    output_html_path = os.path.join(datadir, "records.html")
    fig.write_html(output_html_path)


if not log_files:
    print("No log files found!")
    exit()

if __name__ == "__main__":
    line_df, bubble_df = combined_extract_data(log_files)
    rewards_visualize(line_df)
    memory_visualize(line_df)
    tcp_visualize(line_df)
    logarithmic_bubble_visualize(bubble_df)
    records_visualize(line_df)
