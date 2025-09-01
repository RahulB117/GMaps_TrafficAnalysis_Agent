from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from agent.agent import create_traffic_agent

app = FastAPI(
    title="Google Maps Traffic Agent",
    description="LangChain agent API for live traffic monitoring using Google Maps.",
    version="1.0.0",
)

# # (Optional) Enable CORS for remote frontend access
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],   # For production, restrict this!
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Add agent as a REST API under /agent
agent_executor = create_traffic_agent()
add_routes(app,
           agent_executor,
           path="/agent")

# Health check
@app.get("/")
def root():
    return {"status": "ok", "msg": "LangServe Traffic Agent is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
