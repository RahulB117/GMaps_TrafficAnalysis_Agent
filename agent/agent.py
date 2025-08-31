import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate

from tools import tools

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
     You are a traffic monitoring assistant. Given the user's request, always:
     - Geocode both addresses.
     - Fetch current live traffic for the route.
     - Log the result with timestamp.
     - Return a summary to the user with a color-coded traffic level (Blue, Yellow, Red, Dark Red).
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
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

# ---- Quick Test Script ----
if __name__ == "__main__":
    agent_executor = create_traffic_agent()
    origin = "Whitefield, Bangalore"
    destination = "MG Road, Bangalore"
    interval = "1 min"  # For testing

    user_input = {
        "origin": origin,
        "destination": destination,
        "interval": interval
    }

    print("\n----- AGENT TEST START -----\n")
    result = agent_executor.invoke(user_input)
    print("\n----- AGENT OUTPUT -----\n")
    print(result)