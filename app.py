import streamlit as st
import time
import re
import pandas as pd
import plotly.express as px
from agent.agent import create_traffic_agent



# Parse minutes from agent/tool result
def extract_minutes(duration_str):
    if not duration_str:
        return None
    match = re.match(r"(\d+)", duration_str)
    return int(match.group(1)) if match else None


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

# Agent Loop: Collect Results
if st.session_state['running']:
    agent_executor = create_traffic_agent()
    progress = st.progress(0)
    for i in range(stop_after):
        st.write(f"**Run {i+1} of {stop_after}**")
        user_input = {
            "origin": origin,
            "destination": destination,
            "interval": interval_str
        }
        result = agent_executor.invoke(user_input)
        # For MVP: parse traffic level, durations, and timestamp from agent output (improve as needed)
        summary = result.get('output', '')
        run_data = {
            "Run": i+1,
            "Timestamp": pd.Timestamp.now(),
            "Summary": summary
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
    st.dataframe(df, use_container_width=True)

    # Optionally, parse durations for plotting (simple string split, can improve with regex)
    try:
        df['Travel Time (mins)'] = df['Summary'].str.extract(r"estimated travel time is \*\*(\d+)")
        df['Travel Time (mins)'] = pd.to_numeric(df['Travel Time (mins)'])
        fig = px.line(
            df, 
            x="Timestamp", 
            y="Travel Time (mins)",
            title="Travel Time Over Runs",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("Plot unavailable (could not extract travel time).")

    # Download
    st.download_button("Download CSV", df.to_csv(index=False), "traffic_results.csv", "text/csv")

# --- 4. (Feedback form - PINNED for later) ---
# st.form(...) etc. (to be added in next version)