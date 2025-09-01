import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from agent.tools import tools
from agent.utils import parse_agent_output

# Enable LangSmith/Tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "GMAP_Agent"

# LLM Setup
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

# Appropriate Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", 
 """
 You are a traffic monitoring assistant. Given the user's request of origin and destination, always:
   - Geocode both addresses.
   - Use the `formatted_address` from each GeocodeLocation result as `origin` and `destination` to fetch current live traffic for the route.
   - Pass these as structured arguments
   - After fetching live traffic, log the results and return a JSON object containing:
    - origin: string
    - destination: string
    - interval: string
    - summary: user-friendly markdown summary (1 or 2 lines only)
    - base_duration_mins: integer (travel time without traffic in minutes)
    - travel_time_mins: integer (travel time with current traffic in minutes)
    - traffic_level: string (Blue, Yellow, Red, Dark Red)
    - percent_increase: string (ex - '12.5%')
    - timestamp: ISO8601 string
 Do NOT return plain text—always respond with a JSON object with these fields.
 Only use the available tools. If any step fails, report the error clearly.
 """),
    ("human", 
     """
     Origin: {origin}
     Destination: {destination}
     Interval: {interval}
     """),
    ("placeholder", "{agent_scratchpad}")
])

def create_traffic_agent():
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    # Class InputUnwrapper added to handle input parsing issues
    # Compatibility with LangServe
    class InputUnwrapper(Runnable):
        def invoke(self, input, config=None, **kwargs):
            if isinstance(input, dict) and "input" in input and isinstance(input["input"], dict):
                input = input["input"]
            return executor.invoke(input, config=config, **kwargs)

    return InputUnwrapper()

# Smoke-test
# Modify Line 7 and 8, remove agent.
if __name__ == "__main__":
    agent_executor = create_traffic_agent()
    origin = "Whitefield, Bangalore"
    destination = "MG Road, Bangalore"
    interval = "1 min"

    user_input = {
        "origin": origin,
        "destination": destination,
        "interval": interval
    }

    print("\n##### AGENT TEST START #####\n")
    result = agent_executor.invoke(user_input)
    result_updated = parse_agent_output(result)
    print("\n##### AGENT TEST OUTPUT #####\n")
    print(result_updated)