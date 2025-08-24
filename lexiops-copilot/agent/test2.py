import asyncio
from duckduckgo_search import DDGS
from langchain_mcp_adapters.client import MultiServerMCPClient
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import logging config TRƯỚC tất cả imports khác để tắt debug logs
from agent.utils.logging_config import suppress_debug_logs

from langchain_openai import ChatOpenAI
from agent.settings.config import settings
import asyncio
from langchain_openai import ChatOpenAI
from agent.settings.config import settings
from agent.graph import HierarchicalAgent
from langchain.tools import tool
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import json
import time
from agent.mcp_tools.local_tools import get_current_time, get_current_weather, search_web
from agent.schemas import PlannerOutput, Task
from dataclasses import asdict
from typing import Any, Dict, List
from pydantic import BaseModel, Field, ValidationError

def parse_planner_output(event: Any) -> PlannerOutput:
    messages = event.get("messages") or event.get("mess", {}).get("messages")
    if not messages or len(messages) == 0:
        raise ValueError("No messages found in event")

    msg = messages[0]
    if msg['parsing_error']:
        print("Parsing error occurred")
        if "tool_calls" in msg and len(msg["tool_calls"]) > 0:
            raw_args = msg["tool_calls"][0].get("args")
        # Nếu chưa có, thử lấy từ raw.additional_kwargs
        elif "raw" in msg and hasattr(msg["raw"], "additional_kwargs"):
            tool_calls = msg["raw"].additional_kwargs.get("tool_calls", [])
            if len(tool_calls) > 0:
                arguments_str = tool_calls[0]["function"]["arguments"]
                print(arguments_str)
                return {"parsed": "error","arguments":arguments_str}
    else:
        output_parsed = msg['parsed']
        print("Parsed output:", output_parsed)
        return {"parsed": "pass","arguments":output_parsed}

    # Bổ sung field mặc định nếu thiếu
    # try:
    #     raw_args.setdefault("response", "")
    #     raw_args.setdefault("visible_to_user", False)
    # except Exception as e:
    #     print(f"Error setting default fields: {e}")
    #     print(raw_args)
    #     return PlannerOutput(tasks=[], response="", visible_to_user=False)
        
    # Chuyển tasks sang object Task nếu cần
    # tasks_raw = raw_args.get("tasks", [])
    # tasks = []
    # for t in tasks_raw:
    #     if isinstance(t, Task):
    #         tasks.append(t)
    #     else:
    #         t.setdefault("tool", None)
    #         t.setdefault("params", None)
    #         t.setdefault("depend_on", [])
    #         tasks.append(Task(**t))
    # raw_args["tasks"] = tasks

    # Stop here for debugging
    # print("Parsed raw_args:", raw_args)
    # stoppp
    # # Parse PlannerOutput
    # return PlannerOutput(**raw_args)
def safe_serialize(value):
    try:
        json_output = parse_planner_output(value)
        return json_output
    except Exception as e:
        return {"error": str(e)}




async def run_tests(agent, list_test_case, model_name, log_file="planner_benchmark.json"):
    for i, case in enumerate(list_test_case, 1):
        print(f"\n\n\n=== TEST CASE {i}: {case[:50]}... ===\n")

        start_time = time.time()
        collected_output = []

        async for event in agent.astream(case):
            for key, value in event.items():
                print(f"--- Node: {key} ---")
                print(value)
                print("\n" + "="*40 + "\n")
                collected_output.append({key: value})

        end_time = time.time()
        inference_time_ms = int((end_time - start_time) * 1000)

        # build log entry
        log_entry = {
            "model": model_name,
            "inference_time_ms": inference_time_ms,
            "prompt": case,
            "planner_output": collected_output
        }

        # append to file
        # print(collected_output)
        # with open(log_file, "a", encoding="utf-8") as f:
        #     f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        # print(f"✅ Logged test case {i} → {log_file}")



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
    
    llm =   ChatOpenAI(
        model="gpt-4.1-nano",  
        # model="gpt-5-mini",
        openai_api_key=settings.OPENAI_API_KEY,
        temperature=1,
        verbose=False  # Đảm bảo tắt verbose
    )
    
    mcp_tools = await client.get_tools()
    local_tools = [get_current_time,search_web, get_current_weather]
    all_tools = local_tools + mcp_tools
    agent = HierarchicalAgent(llm, all_tools)
    list_test_case = [
    # "Check logs service A và restart service A nếu pod crash.",
    # "Hãy backup database orders và kiểm tra trạng thái backup thành công hay chưa.",
    # "Tìm kiếm thông tin về 'Thủ tướng Việt Nam hiện tại là ai, Chủ tịch nước hiện tại là ai, nhận chức khi nào'.",
    # "Tìm kiếm thông tin về 'Thủ tướng Việt Nam hiện tại là ai,Chủ tịch nước hiện tại là ai'"
    # "tôi tên là nguyễn văn tính, tôi rất lươn lẹo, nhưng người yêu tôi vẫn yêu tôi vì sao?"
    # "Tôi muốn biết thời tiết hiện tại ở Hồ Chí Minh và Tokyo.",
    "Lấy danh sách các pod đang chạy hiện tại"
]

    await run_tests(agent, list_test_case, model_name="gpt-4.1-nano")

asyncio.run(main())

