from fastapi import FastAPI, HTTPException
from agent.graph import get_graph
from pydantic import BaseModel
from dotenv import load_dotenv

# Import logging config FIRST để tắt debug logs
from agent.utils.logging_config import suppress_debug_logs

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from agent.graph import AgentExecutor
# Load environment variables
load_dotenv()

app = FastAPI(
    title="LexiOps Copilot - AI-Powered MCP Workflow",
    description="An intelligent agent workflow using OpenAI GPT-4 Turbo and MCP tools",
    version="2.0.0"
)

llm_planner = ChatOpenAI(model="gpt-5.1-nano")

# Khởi tạo MCP Client
mcp_client = MultiServerMCPClient(
    {
        "shell": {
            "command": "python",
            "args": ["agent\\mcp_tools\\mcp_server.py"],
            "transport": "stdio",
        }
    }
)

# Global graph instance
graph = None

class UserRequest(BaseModel):
    message: str

class AgentResponse(BaseModel):
    response: str
    status: str
    tool_results: list = []

@app.on_event("startup")
async def startup_event():
    """Initialize the workflow graph on startup"""
    global graph
    try:
        print("🚀 Initializing LexiOps Copilot...")
        graph = await AgentExecutor.create(llm_planner, mcp_client)
        print("✅ Agent ready!")
    except Exception as e:
        print(f"❌ Failed to initialize graph: {e}")
        raise

@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(request: UserRequest):
    """Main endpoint to chat with the agent"""
    if not graph:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Prepare initial state
        initial_state = {
            "input": request.message,
            "messages": [],
            "plan": None,
            "tool_results": [],
            "final_response": "",
            "current_step": "starting"
        }
        
        print(f"🔄 Processing: {request.message[:50]}...")
        
        # Run the workflow
        final_state = None
        async for output in graph.astream(initial_state):
            for node_name, node_output in output.items():
                print(f"📍 {node_name.upper()}: {list(node_output.keys())}")
                final_state = node_output
        
        if not final_state or "final_response" not in final_state:
            raise HTTPException(status_code=500, detail="Workflow did not complete properly")
        
        return AgentResponse(
            response=final_state["final_response"],
            status="success",
            tool_results=final_state.get("tool_results", [])
        )
        
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if graph else "initializing",
        "service": "LexiOps Copilot"
    }

@app.get("/")
async def root():
    """Root endpoint with usage instructions"""
    return {
        "message": "LexiOps Copilot API",
        "endpoints": {
            "chat": "POST /chat - Chat with the agent",
            "health": "GET /health - Check service health"
        },
        "example_requests": [
            "What time is it?",
            "Read a file for me", 
            "Show me system info"
        ]
    }