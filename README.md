# 🚦 Google Maps Agentic Traffic Monitor

## Situation

As residents of Bangalore (or any traffic-heavy city), we constantly face unpredictable and frustrating commutes. Knowing the best time to leave rather than just guessing can save hours and greatly reduce daily stress. Existing apps show live traffic but there’s no easy way to autonomously track, log, and analyze trends for specific routes to make data-driven commute decisions.

## Task

**Goal:**  
Build an autonomous AI-powered system that:
- Monitors Google Maps traffic conditions for any route at customizable intervals.
- Logs real time and historical traffic data (duration, traffic color/level, percent increase).
- Visualizes trends and enables users to download their commute data for further analysis.
- Empowers both commuters and researchers to discover optimal travel times and traffic patterns.

## Action

- Designed and implemented a multi-step agent using [LangChain](https://python.langchain.com/) and Google Maps APIs (geocode, directions/traffic).
- Engineered robust tools with strict Pydantic schemas for argument safety ensuring structured data flow between agent steps.
- Integrated a Streamlit UI to:
  - Accept user input (origin, destination, interval, stop condition)
  - Orchestrate interval-based agent runs with clear progress and status updates
  - Visualize results (travel time, traffic level) with color coded, interactive graphs
  - Export results as CSV for further use
- Added comprehensive logging and error handling for reliability.
- Connected to LangSmith for full agent monitoring and evaluation pipeline.

## Result

- The system enables any user to track and analyze traffic on their chosen route, spot trends and plan optimal departures turning traffic frustration into actionable data.
- All agent actions are fully auditable and observable through LangSmith.
- The architecture is robust and easily extensible (feedback forms, notifications, multi-user support, cloud deployment)

---

## Quickstart: How to Run Locally

### **Prerequisites**
- Python 3.9+
- [Google Maps API key](https://developers.google.com/maps/documentation/javascript/get-api-key)
- [OpenAI API key](https://platform.openai.com/api-keys) (for agent reasoning)
- All dependencies installed via pip

### **Setup**
1. **Clone the repo and enter the folder:**
   ```bash
   mkdir gmap-traffic-agent
   cd gmap-traffic-agent
   git clone https://github.com/RahulB117/GMaps_TrafficAnalysis_Agent.git
   ```
2. **Add your API keys and LangSmith project name to a .env file:**
   ```bash
   OPENAI_API_KEY=
   GOOGLE_MAPS_API_KEY=
   LANGCHAIN_API_KEY=
   LANGCHAIN_PROJECT=
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
4. **Run the app from root directory:**
   ```bash
   streamlit run app.py
   ```
- Follow the UI prompts to enter your route, select interval, and run monitoring.
- View and download your results and plots.

### Project Structure
```bash
/agent/
  agent.py        # Agent orchestration & schema enforcement
  tools.py        # Tool implementations
  utils.py        # Output parsing/guardrails
app.py            # Streamlit UI
data/             # Generated logs and downloads
```
### Features
- Schema-guarded tool orchestration
- Structured JSON agent output for easy analysis and export
- Color-coded traffic analytics
- LangSmith monitoring and eval integration
- Designed for cloud deployment (LangServe ready)

### Next Steps
- Add user feedback and notification modules
- Plug into LangSmith feedback API for crowd-sourced evaluation
- Deploy via LangServe for multi-user access

### Author
Built by Rahul Babu | https://www.linkedin.com/in/rahul-babu117/

### License
