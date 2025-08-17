"""
Updated brain.py with environment-based configuration and service discovery
"""
import json
import re
import asyncio
import os
from openai import AsyncOpenAI
from app.config.database import db_async, analysis_results_col, messages_col
from app.config.api_client import api_client
from app.config.settings import cfg_settings
from app.utils.utils_essential import current_time
from typing import Generator
from fastapi.responses import StreamingResponse, JSONResponse
import logging
import traceback

# Basic logging instead of basicConfig
logger = logging.getLogger(__name__)

# Initialize OpenAI client with environment variable
client = AsyncOpenAI(api_key=cfg_settings.OPENAI_API_KEY)

system_prompt = {
    "role": "system",
    "content": "bạn là một trợ lý AI có khả năng lý luận theo từng bước"
}

# === Prompt Template ===
PROMPT_TEMPLATE = '''
Hiện tại là {current_time}.
Bạn là một hệ thống Phân tích câu hỏi người dùng và trả lời nhiệm vụ:
1. Phân tích câu hỏi của người dùng.
2. Quyết định có cần gọi công cụ (tool) để hỗ trợ trả lời hay không.
3. Khi dùng công cụ, luôn phải gọi web_search. Nếu cần thêm thông tin từ dữ liệu pháp luật, có thể kèm theo laws_retrieval.

Yêu cầu:
- Luôn trả về kết quả ở định dạng JSON hợp lệ và chỉ chứa một JSON duy nhất.
- Không xuống dòng trong các giá trị chuỗi (string) bên trong JSON.
- Nếu không cần công cụ, trả về `"actions": []`.
- Các công cụ hợp lệ:
- `web_search`: Khi thông tin cần cập nhật và luôn ưu tiên tìm kiếm web.
- `laws_retrieval`: Khi thông tin có thể tìm thấy ở kho dữ liệu pháp luật.

Output mẫu:
```json
{{
  "analysis": {{
    "rewritten_query": "luật đất đai 2025",
    "query_type": "single",
    "reasoning": "Câu hỏi liên quan tới luật đất đai 2025 cần thông tin mới nhất từ internet và dữ liệu pháp luật."
  }},
  "actions": [
    {{
      "tool": "web_search",
      "input": "luật đất đai 2025 Việt Nam",
      "reason": "Thông tin cần tham khảo thêm."
    }},
    {{
      "tool": "laws_retrieval",
      "input": "luật đất đai 2025",
      "reason": "Thông tin có thể tìm thấy trong kho dữ liệu pháp luật."
    }}
  ],
  "final_answer":"Luật đất đai 2025 quy định về việc sử dụng đất đai, quyền và nghĩa vụ của người sử dụng đất, cũng như các quy định liên quan đến quản lý đất đai."
}}
Câu hỏi của người dùng: {query}
'''

def clean_json_from_response(content: str) -> str:
    """Extract JSON from LLM response"""
    json_match = re.search(r'{[\s\S]*}', content)
    if not json_match:
        raise ValueError("Không tìm thấy JSON hợp lệ trong phản hồi.")
    return json_match.group(0)

async def analyze_user_query(
    conversation_id: str, 
    user_id: str, 
    query: str, 
    model: str = None
):
    """Analyze user query with environment-based configuration"""
    model = model or cfg_settings.DEFAULT_LLM_MODEL
    prompt = PROMPT_TEMPLATE.format(current_time=current_time(), query=query.strip())

    try:
        # Call LLM API
        completion = await client.chat.completions.create(
            model=model,
            messages=[system_prompt, {"role": "user", "content": prompt}],
            temperature=0.3,
            stop=["Observation:"]
        )

        # Parse LLM response
        raw_text = completion.choices[0].message.content.strip()
        raw_text = clean_json_from_response(raw_text)
        logger.info(f"LLM raw output: {raw_text}")
        
        try:
            llm_output = json.loads(raw_text)
            # Trigger tools asynchronously
            asyncio.create_task(
                trigger_tools_and_combine_results(llm_output, conversation_id, user_id)
            )
        except json.JSONDecodeError as e:
            logger.error(f"LLM output không phải JSON hợp lệ: {e}")
            return JSONResponse(
                {"error": "Invalid LLM JSON output", "raw_output": raw_text}, 
                status_code=500
            )
        except Exception as e:
            logger.error(f"Lỗi khi xử lý LLM output: {e}\n{traceback.format_exc()}")
            return JSONResponse(
                {"error": str(e), "raw_output": raw_text}, 
                status_code=500
            )

        # Save to database
        await db_async.analysis_results.insert_one({
            "conversation_id": conversation_id,
            "user_id": user_id,
            "question": query,
            "role": "assistant",
            "text": llm_output,
            "created_at": current_time(),
            "is_reused": False,
            "model": model
        })

        return JSONResponse(llm_output)

    except Exception as e:
        logger.error(f"[LLM Error] {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)

async def trigger_tools_and_combine_results(
    llm_output: dict, 
    conversation_id: str, 
    user_id: str
):
    """Trigger tools using centralized API client"""
    actions = llm_output.get("actions", [])
    combined_results = {}
    use_web_search = False
    use_retrieval = False

    for action in actions:
        tool = action.get("tool")
        input_text = action.get("input")

        try:
            if tool == "web_search":
                use_web_search = True
                await api_client.web_search(input_text)
                combined_results[tool] = True
                
            elif tool == "laws_retrieval":
                use_retrieval = True
                await api_client.laws_retrieval(input_text)
                combined_results[tool] = True
                
            else:
                combined_results[tool] = {"error": "Unknown tool"}
                
        except Exception as e:
            logger.error(f"Error calling {tool}: {str(e)}")
            combined_results[tool] = {"error": str(e)}

    # Generate response
    rewrite_query = llm_output.get("analysis", {}).get("rewritten_query", "")
    generate_payload = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "rewrite_query": rewrite_query,
        "use_web_search": use_web_search,
        "use_retrieval": use_retrieval
    }

    try:
        await api_client.generate_response(generate_payload)
    except Exception as e:
        logger.error(f"Error in generate_response: {str(e)}")

    return combined_results
