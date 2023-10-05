import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
import glob
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

user_home = os.path.expanduser("~")
datadir = os.path.join(user_home, ".local", "share", "safe", "tools", "ntracking")

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
    filenames = sorted(filenames)
    all_data = []

    for file_number, filename in enumerate(filenames):
        with open(filename, "r") as file:
            lines = file.readlines()

        formats = {
            "Memory used": "float_mb",
            "Records": "int",
            "Disk usage": "float_mb",
            "CPU usage": "float_percent",
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

    # DataFrame for rewards_visualize and memory_visualize
    line_df = pd.DataFrame(all_data)
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
custom_hovertemplate = "%{customdata[6]}<br>" + \
                       "PID: %{customdata[7]}<br>"+ \
                       "Records: %{customdata[1]}<br>" + \
                       "Disk used: %{customdata[2]}MB<br>" + \
                       "CPU: %{customdata[4]:.2f}%<br>"

def rewards_visualize(df):
    Number_to_color = generate_Number_to_color(sorted(df['Number'].unique()))
    fig = px.line(df, x="Timestamp", y="Rewards balance", color="Number", line_group="Number",
        custom_data=["Number", "Records", "Disk usage", "Memory used", "CPU usage", "Rewards balance", "Node", "PID"],
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
                    #dict(count=30, label="30 days", step="day", stepmode="backward"),
                    #dict(count=3, label="3 months", step="month", stepmode="backward"),
                    #dict(count=6, label="6 months", step="month", stepmode="backward"),
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
        custom_data=["Number", "Records", "Disk usage", "Memory used", "CPU usage", "Rewards balance", "Node", "PID"],
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
                    #dict(count=7, label=" Week", step="day", stepmode="backward"),
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
        custom_data=["Number", "Records", "Disk usage", "Memory used", "CPU usage", "Rewards balance", "Node", "PID"],
        labels={"Memory": "Memory Usage (MB)"},
        color_discrete_map=Number_to_color)


    # Hide the x-axis labels (Timestamp)
    fig.update_layout(
        xaxis_title_text="TCP connections (established)",
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
                    #dict(count=7, label=" Week", step="day", stepmode="backward"),
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
                 hover_data=["Number", "Node", "Number", "Rewards balance", "Records"],
                 labels={"log_rewards": "Rewards Balance"},
                 color_discrete_map=Number_to_color,
                 size_max=100)
    
    fig.update_traces(
        hovertemplate="Number: %{customdata[0]}<br>Node: %{customdata[1]}<br>Number: %{customdata[2]}<br>Rewards balance: %{customdata[3]:.9f}<br>Records: %{customdata[4]}<extra></extra>",  # Added Records here
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
    fig.update_traces(hovertemplate="Number: %{customdata[0]}<br>Node: %{customdata[1]}<br>Rewards balance: %{customdata[3]:.9f}<br>Records: %{customdata[4]}<extra></extra>")

    output_html_path = os.path.join(datadir, "bubble_rewards.html")
    fig.write_html(output_html_path) 

log_files = glob.glob(os.path.join(datadir, "resources*.log"))

def get_durations_since_last_change():
    log_files = glob.glob(os.path.join(datadir, "resources*.log"))
    
    if not log_files:
        print("No log files found!")
        return
    

    grouped_df = line_df.groupby("Node").apply(lambda x: x.sort_values("Timestamp", ascending=False)).reset_index(drop=True)
    
    # Store durations of no change for each node
    no_change_durations = []

    # For each node, calculate the duration since the last change in "Rewards balance"
    for node, group in grouped_df.groupby("Node"):
        last_reward = None
        last_timestamp = None
        for idx, row in group.iterrows():
            if last_reward is None:
                last_reward = row["Rewards balance"]
                last_timestamp = row["Timestamp"]
                continue
            
            if row["Rewards balance"] != last_reward:
                duration = last_timestamp - row["Timestamp"]
                no_change_durations.append({
                    "Node": node,
                    "Number": row["Number"],
                    "PID": row["PID"],
                    "Records": row["Records"],
                    "Rewards balance": row["Rewards balance"],
                    "Duration": duration
                })
                break
    
    # Convert the list to a DataFrame and sort by Duration
    durations_df = pd.DataFrame(no_change_durations).sort_values(by="Duration")
    
    # Get the 20 most recent and 10 least recent durations
    most_recent = durations_df.head(20)
    least_recent = durations_df.tail(20)
    
    return most_recent, least_recent

file_list = glob.glob(os.path.join(datadir, "resources*.log"))
line_df, _ = combined_extract_data(file_list)

most_recent, least_recent = get_durations_since_last_change()

desired_columns_order = ['PID', 'Number', 'Node', 'Records', 'Rewards balance', 'Duration']

print("15 Most recent rewarded nodes:")
print(most_recent[desired_columns_order].to_string(index=False))

print("\n15 Biggest skivers. :")
print(least_recent[desired_columns_order].to_string(index=False))

def visualize_durations(most_recent, least_recent):
    all_Number = pd.concat([most_recent['Number'], least_recent['Number']]).unique()
    Number_to_color = generate_Number_to_color(sorted(all_Number))

    fig = go.Figure()

    hovertemplate = (
        "Node: %{x}<br>" +
        "PID: %{customdata[0]}<br>" +
        "Number: %{customdata[1]}<br>" +
        "Records: %{customdata[2]}<br>" +
        "Rewards Balance: %{customdata[3]}<br>" +
        "Duration: %{y:.2f} hours<br>"
    )

    # Plot most recent durations
    fig.add_trace(go.Bar(
        x=most_recent['Node'],
        y=most_recent['Duration'].dt.total_seconds() / (60*60),  # Convert timedelta to hours
        name='Most Recent',
        marker_color=[Number_to_color[Number] for Number in most_recent['Number']],
        customdata=most_recent[['PID', 'Number', 'Records', 'Rewards balance']],
        hovertemplate=hovertemplate
    ))

    # Plot least recent durations
    fig.add_trace(go.Bar(
        x=least_recent['Node'],
        y=least_recent['Duration'].dt.total_seconds() / (60*60),  # Convert timedelta to hours
        name='Least Recent',
        marker_color=[Number_to_color[Number] for Number in least_recent['Number']],
        customdata=least_recent[['PID', 'Number', 'Records', 'Rewards balance']],
        hovertemplate=hovertemplate
    ))

    # Update layout
    fig.update_layout(
        xaxis_title_text="",
        yaxis_title_text="",
        hovermode='closest',
        paper_bgcolor='#252526',
        plot_bgcolor='#070D0D',
        margin=dict(t=32, b=32, l=32, r=32, pad=2),
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(
            showgrid=False, 
            visible=True,
            tickcolor='#ffffff',
            tickfont=dict(color='#ffffff')
        ),
        legend_title_font_color='#ffffff',
        legend_font_color='#ffffff',
        hoverlabel=dict(bgcolor='#252526', font=dict(color='#ffffff')),
        barmode='group',
        showlegend=False
    )
    fig.add_annotation(
    text="<-- 20 Most recent <-- Time elapsed since last Reward --> 20 Least Recent -->",
    xref="paper", yref="paper",
    x=0.5, y=-0.01,  # position the text
    showarrow=False,
    yanchor="top",  # anchor the text
    font=dict(size=14, color="#ffffff") 
    )

    output_html_path = os.path.join(datadir, "durations.html")
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
    visualize_durations(most_recent, least_recent)

