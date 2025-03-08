import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

# Import your actual agent
from agent import create_agent, AgentState

app = FastAPI(title="LangGraph Agent API")

# Add CORS middleware to allow LangGraph Studio to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to LangGraph Studio domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = create_agent()

class AgentInput(BaseModel):
    input: str
    config: Optional[Dict[str, Any]] = None

class AgentStateModel(BaseModel):
    state: Dict[str, Any]

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "LangGraph Agent is running"}

@app.post("/run")
async def run_agent(agent_input: AgentInput):
    """Run the agent with the given input and return the result."""
    try:
        # Run the agent
        result = agent.invoke({"input": agent_input.input, **(agent_input.config or {})})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@app.post("/run_stream")
async def run_agent_stream(agent_input: AgentInput):
    """Stream the agent's execution with the given input."""
    try:
        # Stream the agent's execution
        events = []
        for event in agent.stream({"input": agent_input.input, **(agent_input.config or {})}):
            events.append(event)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@app.get("/schema")
async def get_schema():
    """Return the agent's schema for LangGraph Studio."""
    try:
        # Get the graph's schema - this is useful for LangGraph Studio
        schema = agent.get_graph().schema
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True) 