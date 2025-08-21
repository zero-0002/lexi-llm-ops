from langchain_core.messages import AIMessage, ToolCall, HumanMessage
from langchain_openai import ChatOpenAI
from agent.state import AgentState
from agent.utils.json_parser import JSONParser
import json
import os
import re
import logging
from agent.nodes.prompt.planner_prompt import planning_prompt

logger = logging.getLogger(__name__)


def planner_node(state: AgentState) -> dict:
    """
    Tạo kế hoạch thông minh sử dụng OpenAI GPT-4 Turbo với dynamic tools
    """
    logger.info(f"--- PLANNER: Analyzing input with GPT-4 Turbo: '{state['input'][:50]}...' ---")
    
    # Initialize OpenAI model
    llm = ChatOpenAI(
        model="gpt-5-nano",  # GPT-5 Nano
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = planning_prompt['prompt_2']

    try:
        # Get AI planning response
        response = llm.invoke(prompt.format(input=state['input']))
        
        # Parse the AI response using improved JSON extraction
        ai_content = response.content.strip()
        logger.info(f"AI Raw Response: {ai_content[:150]}...")
        with open("response_raw_plan.txt", "w", encoding="utf-8") as f:
            f.write(ai_content)
        
        # Use advanced JSONParser
        plan = JSONParser.parse_json_response(ai_content)
        logger.info(f"Extracted Plan: {plan}")

        # Convert from new format to old format if needed
        if "tool_calls" in plan and "tools_to_use" not in plan:
            plan["tools_to_use"] = plan["tool_calls"]
            plan["reasoning"] = plan.get("thought", "AI generated plan")
        
        # Validate plan structure
        if not isinstance(plan, dict) or "tools_to_use" not in plan:
            raise ValueError(f"Invalid plan structure: {plan}")

        if not isinstance(plan["tools_to_use"], list) or len(plan["tools_to_use"]) == 0:
            raise ValueError("tools_to_use must be a non-empty list")
            
    except Exception as e:
        logger.error(f"Error during planning: {e}")
        return {
            "messages": [
                AIMessage(content=f"❌ Lỗi khi tạo kế hoạch: {str(e)}")
            ],
            "plan": None,
            "current_step": "planning_failed"
        }
    
    # Tạo tool calls cho ToolNode
    tool_calls = []
    for i, tool in enumerate(plan["tools_to_use"]):
        tool_calls.append(
            ToolCall(
                name=tool["name"],
                args=tool["args"],
                id=f"tool_call_{i+1}"
            )
        )
    
    # Add human message và AI message với tool calls
    messages = [
        HumanMessage(content=state['input']),
        AIMessage(content=f"I'll help you with that. Plan: {plan['reasoning']}", tool_calls=tool_calls)
    ]
    
    return {
        "messages": messages,
        "plan": plan,
        "current_step": "planning_complete"
    }