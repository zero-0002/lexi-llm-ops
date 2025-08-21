from agent.state import AgentState
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
import os
import json

def synthesizer_node(state: AgentState) -> dict:
    """
    Tổng hợp kết quả từ các tool thành response cuối cùng sử dụng GPT-4 Turbo
    """
    print("--- SYNTHESIZER: Creating intelligent response with GPT-4 Turbo ---")
    
    # Initialize OpenAI model
    llm = ChatOpenAI(
        model="gpt-4.1-nano", 
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Lấy tool results từ messages
    tool_results = []
    for msg in state['messages']:
        if isinstance(msg, ToolMessage):
            tool_results.append({
                "tool_call_id": msg.tool_call_id,
                "content": msg.content,
                "name": getattr(msg, 'name', 'unknown_tool')
            })
    
    # Lấy plan và user input
    plan = state.get('plan', {})
    user_input = state.get('input', '')
    
    # Create synthesis prompt
    synthesis_prompt = f"""
    You are a helpful AI assistant. Create a natural, helpful response to the user based on the following information:
    
    User's original request: "{user_input}"
    
    Plan that was executed: {plan.get('reasoning', 'No plan available')}
    
    Tool results:
    {json.dumps(tool_results, indent=2) if tool_results else "No tool results available"}
    
    Please create a natural, helpful response that:
    1. Directly addresses the user's request
    2. Incorporates the tool results in a natural way
    3. Is conversational and friendly
    4. Provides clear, useful information
    
    Don't use technical jargon or mention "tool execution". Just provide a helpful response as if you naturally know this information.
    """
    
    try:
        # Get AI-generated response
        ai_response = llm.invoke(synthesis_prompt)
        final_response = ai_response.content.strip()
        
        print(f"AI-generated response: {final_response[:100]}...")
        
    except Exception as e:
        print(f"AI Synthesis failed: {e}. Falling back to template response.")
        
        # Fallback to template-based response
        reasoning = plan.get('reasoning', 'Completed requested actions')
        final_response = f"✅ **Task Completed**: {reasoning}\n\n"
        
        if tool_results:
            final_response += "**Results:**\n"
            for i, result in enumerate(tool_results, 1):
                final_response += f"\n{i}. **Tool**: {result.get('name', 'Unknown')}\n"
                final_response += f"   **Output**: {result['content']}\n"
        else:
            final_response += "No tool results available."
    
    return {
        "final_response": final_response,
        "tool_results": tool_results,
        "current_step": "completed"
    }