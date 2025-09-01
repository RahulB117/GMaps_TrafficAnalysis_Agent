import streamlit as st
import time
import re
import os
import pandas as pd
import plotly.express as px
from langserve import RemoteRunnable
from agent.agent import create_traffic_agent
from agent.utils import parse_agent_output
from dotenv import load_dotenv

# Added compatibility for LangServe
load_dotenv()
AGENT_ENDPOINT_URL = os.getenv("AGENT_ENDPOINT_URL", "http://localhost:8000/agent")
agent_executor = RemoteRunnable(AGENT_ENDPOINT_URL)

color_map = {
    "Blue": "#3498db",       # Light blue
    "Yellow": "#f1c40f",     # Yellow
    "Red": "#e74c3c",        # Red
    "Dark Red": "#8B0000",   # True dark red
    None: "#95a5a6",         # Gray for unknown/missing
}


st.title("Google Maps Agentic Traffic Monitor")

# User Inputs
origin = st.text_input("Origin (e.g. Whitefield, Bangalore)")
destination = st.text_input("Destination (e.g. MG Road, Bangalore)")
interval_str = st.selectbox("Interval", 
                            ["1 min", "15 min", "30 min", 
                             "1 hour", "2 hours", "4 hours", 
                             "8 hours", "12 hours", "1 day"])

if "min" in interval_str:
    stop_unit = "minutes"
    interval_seconds = 60 * int(interval_str.split()[0])
elif "hour" in interval_str:
    stop_unit = "hours"
    interval_seconds = 3600 * int(interval_str.split()[0])
else:
    stop_unit = "days"
    interval_seconds = 86400 * int(interval_str.split()[0])

stop_after = st.number_input(f"Stop after ({stop_unit})", min_value=1, value=3)

if "run_results" not in st.session_state:
    st.session_state["run_results"] = []

if st.button("Start Monitoring") and origin and destination:
    st.session_state['running'] = True
    st.session_state["run_results"] = []

if st.button("Stop Monitoring"):
    st.session_state['running'] = False

if 'running' not in st.session_state:
    st.session_state['running'] = False

# Agent Loop
if st.session_state['running']:
    progress = st.progress(0)
    for i in range(stop_after):
        st.write(f"**Run {i+1} of {stop_after}**")
        # Changed input parser due to LangServe compatibility
        user_input = {
            "input": {
                "origin": origin,
                "destination": destination,
                "interval": interval_str
            }
        }
        result = agent_executor.invoke(user_input)
        result = parse_agent_output(result)
        run_data = {
            "Run": i+1,
            "Timestamp": pd.Timestamp.now(),
            "Summary": result.get('summary', ''),
            "Base Duration (mins)": result.get('base_duration_mins', None),
            "Travel Time (mins)": result.get('travel_time_mins', None),
            "Traffic Level": result.get('traffic_level', None),
            "Percent Increase": result.get('percent_increase', None),
            "Origin": result.get('origin', ''),
            "Destination": result.get('destination', ''),
            "Interval": result.get('interval', ''),
            "Timestamp (Agent)": result.get('timestamp', None),
        }
        st.session_state["run_results"].append(run_data)

        progress.progress((i+1)/stop_after)
        if i < stop_after - 1:
            time.sleep(interval_seconds)
    st.session_state['running'] = False
    st.success("Monitoring complete!")

# Display Results Table and Plot
if st.session_state["run_results"]:
    df = pd.DataFrame(st.session_state["run_results"])
    st.subheader("Run Results Table")
    st.dataframe(df, width='stretch')

    # Parse durations for plotting
    try:
        fig = px.scatter(
            df,
            x="Timestamp",
            y="Travel Time (mins)",
            color="Traffic Level",
            color_discrete_map=color_map,
            title="Travel Time with Traffic Level",
            labels={"Travel Time (mins)": "Travel Time (mins)"}
        )
        fig.add_traces(px.line(
            df, x="Timestamp",
            y="Base Duration (mins)",
            line_shape="linear"
            ).data)
        st.plotly_chart(fig, width='stretch')

    except Exception as e:
        st.info("Plot unavailable (could not extract travel time).")
        st.download_button("Download CSV", df.to_csv(index=False), "traffic_results.csv", "text/csv")