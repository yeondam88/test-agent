import os
from typing import Dict, Any, List, Annotated, TypedDict, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import (
    AIMessage,
    HumanMessage,
)
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Define the agent state
class AgentState(TypedDict):
    input: str
    messages: List[Dict[str, Any]]
    output: str

# Create a simple agent builder function
def create_agent():
    """Create a simple LangGraph agent."""
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Define nodes
    def generate_response(state: AgentState) -> Dict:
        """Generate a response to the user's input."""
        messages = state["messages"]
        response = llm.invoke(messages)
        return {"messages": messages + [response.dict()], "output": response.content}
    
    # Define the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("generate_response", generate_response)
    
    # Add edges
    workflow.set_entry_point("generate_response")
    workflow.add_edge("generate_response", END)
    
    # Compile the graph
    agent = workflow.compile()
    
    return agent

# Example usage (for testing)
if __name__ == "__main__":
    agent = create_agent()
    result = agent.invoke({
        "input": "What's the capital of France?",
        "messages": [
            {"type": "human", "content": "What's the capital of France?"}
        ],
        "output": ""
    })
    print(result["output"]) 