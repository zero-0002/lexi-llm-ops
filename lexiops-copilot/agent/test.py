import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.chat_models import init_chat_model
import os
from langchain_openai import ChatOpenAI
from settings.config import settings


async def main():
    client = MultiServerMCPClient(
        {
            "shell": {
                "command": "python",
                "args": ["agent\\mcp_tools\\mcp_server.py"],
                "transport": "stdio",
            }
        }
    )
    
    model =   ChatOpenAI(
        model="gpt-5-nano",  
        openai_api_key=settings.OPENAI_API_KEY
    )
    
    tools = await client.get_tools()

    # 3️⃣ Node gọi model
    def call_model(state: MessagesState):
        response = model.bind_tools(tools).invoke(state["messages"])
        return {"messages": response}

    # 4️⃣ Xây dựng LangGraph workflow
    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_node(ToolNode(tools))
    
    
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    # builder.add_edge("tools", "call_model")
    
    graph = builder.compile()

    # 5️⃣ Ví dụ prompt LLM gửi shell command
    shell_prompt = "Hãy thực thi lệnh kiểm tra pod trên Kubernetes"

    output = await graph.ainvoke({"messages": shell_prompt})
    print("Output:", output)

asyncio.run(main())
