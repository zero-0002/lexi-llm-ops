# /nodes/expert_executor.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage, SystemMessage
from agent.state import AgentState
from agent.schemas import ToolOutputEnvelope
from langgraph.prebuilt import ToolNode
from agent.utils.utils import parse_output_llm
import json
from pydantic import BaseModel
import re, ast, json

class ExecutorNode:
    """
    Node Executor này là một LLM Agent chuyên gia.
    Nó nhận kế hoạch từ Planner và tự quyết định cách thực thi tốt nhất
    bằng các tool đã được bind vào nó.
    """
    def __init__(self, llm, mcp_tools, max_retries: int = 3):
        """
        Khởi tạo Executor với LLM và bộ tool MCP chuẩn.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "Bạn là một Kỹ sư Thực thi AI chuyên nghiệp. "
             "Nhiệm vụ của bạn là nhận một task có mô tả và chiến lược gợi ý, "
             "sau đó chọn công cụ chính xác nhất từ bộ công cụ MCP của bạn để hoàn thành nó. "
             "Hãy suy nghĩ và tạo ra một tool call duy nhất để thực hiện nhiệm vụ được giao."),
            ("human", 
             "Hãy thực hiện nhiệm vụ sau:\n"
             "- Mô tả: {description}\n"
             "- Hướng dẫn: Hãy chọn công cụ phù hợp nhất từ bộ công cụ MCP của bạn và tạo một tool call duy nhất để thực hiện nhiệm vụ này."),
        ])
        
        self.executor_llm = llm.bind_tools(mcp_tools)
        self.chain = prompt | self.executor_llm
        self.tools = mcp_tools
        self.max_retries = max_retries

    def __call__(self, state: AgentState) -> dict:
        print("--- NODE: EXPERT EXECUTOR ---")
        
        plan = state.get("plan")
        if not plan or not plan.tasks:
            return {}

        processed_results = []
        tool_executor = ToolNode(self.tools)

        for task in plan.tasks:
            print(f"--> Đang thực thi Task ID: {task.task_id} - {task.description}")

            # B1: sinh tool call lần đầu từ chain
            ai_message_with_tool_call = self.chain.invoke({
                "description": task.description
            })

            retries = 0
            tool_output = None

            # Chuẩn bị history cho retry
            retry_messages = [
                SystemMessage(content="Bạn là một Kỹ sư Thực thi AI chuyên nghiệp. "
                    "Nhiệm vụ của bạn là nhận một task có mô tả và chiến lược gợi ý, "
                    "sau đó chọn công cụ chính xác nhất từ bộ công cụ MCP của bạn để hoàn thành nó. "
                    "Hãy suy nghĩ và tạo ra một tool call duy nhất để thực hiện nhiệm vụ được giao."),
                HumanMessage(content=f"Hãy thực hiện nhiệm vụ sau:\n"
                    f"- Mô tả: {task.description}\n"
                    f"- Hướng dẫn: Hãy chọn công cụ phù hợp nhất từ bộ công cụ MCP của bạn và tạo một tool call duy nhất để thực hiện nhiệm vụ này."),
                AIMessage(content=parse_output_llm(ai_message_with_tool_call,name=True))
            ]

            # B2: retry loop
            while retries <= self.max_retries:
                tool_result_message = tool_executor.invoke(
                    {"messages": [ai_message_with_tool_call]}
                )
                first_tool_message = tool_result_message['messages'][0]
                raw_content = first_tool_message.content

                tool_output = normalize_tool_output(raw_content)

                if tool_output.status == "success":
                    break
                else:
                    print(f"[Retry {retries}] Tool call thất bại: {tool_output.error_message}")
                    retries += 1
                    if retries > self.max_retries:
                        break

                    # append lỗi vào history
                    retry_messages.append(HumanMessage(
                        content=f"Tool call bị lỗi:\n{tool_output.error_message}\n"
                                f"Hãy sửa lại tool call cho hợp lệ và chỉ trả về tool call."
                    ))

                    # gọi lại model với full history
                    
                    ai_message_with_tool_call = self.executor_llm.invoke(retry_messages)
                    raw_ai_message = AIMessage(content=parse_output_llm(ai_message_with_tool_call))
                    retry_messages.append(raw_ai_message)

            # B3: đóng gói kết quả
            if tool_output and tool_output.status == "success":
                data_payload = tool_output.data
                if isinstance(data_payload, BaseModel):
                    data_str = data_payload.model_dump_json(indent=2)
                else:
                    try:
                        data_str = json.dumps(data_payload, indent=2, ensure_ascii=False)
                    except TypeError:
                        data_str = str(data_payload)

                result_content_for_planner = (
                    f"Kết quả của Task ID {task.task_id}: THÀNH CÔNG\n"
                    f"Data:\n{data_str}"
                )
            else:
                result_content_for_planner = (
                    f"Kết quả của Task ID {task.task_id}: THẤT BẠI\n"
                    f"Lỗi: {tool_output.error_message if tool_output else 'Không rõ'}"
                )

            processed_results.append(result_content_for_planner)
        final_message = HumanMessage(
            content="[Báo cáo từ Executor]\nĐã hoàn thành thực thi kế hoạch. Dưới đây là kết quả:\n" + "\n".join(processed_results)
        )

        return {"messages": [final_message]}



def normalize_tool_output(raw_content) -> ToolOutputEnvelope:
    """
    Chuẩn hoá output từ ToolNode thành ToolOutputEnvelope.
    Hỗ trợ các trường hợp:
    - ToolOutputEnvelope gốc
    - dict
    - JSON string
    - repr string ("status='success' error_message=None data=[{...}]")
    """
    if isinstance(raw_content, ToolOutputEnvelope):
        return raw_content

    elif isinstance(raw_content, dict):
        return ToolOutputEnvelope(**raw_content)

    elif isinstance(raw_content, str):
        
        if "status" not in raw_content.lower():
            return ToolOutputEnvelope(
                status="error",
                error_message=f"Unparseable content: {raw_content}",
                data=None
            )

        # thử parse JSON trước
        try:
            return ToolOutputEnvelope.parse_raw(raw_content)
        except Exception:
            # nếu fail → thử parse kiểu repr
            try:
                status_match = re.search(r"status='([^']+)'", raw_content)
                error_match = re.search(r"error_message=(None|'[^']*')", raw_content)
                data_match = re.search(r"data=(.+)", raw_content)

                status = status_match.group(1) if status_match else "error"
                error_message = None
                if error_match:
                    err_val = error_match.group(1)
                    error_message = None if err_val == "None" else err_val.strip("'")

                data = None
                if data_match:
                    data_str = data_match.group(1).strip()
                    try:
                        data = ast.literal_eval(data_str)
                    except Exception:
                        data = data_str  # giữ nguyên nếu không parse được

                return ToolOutputEnvelope(
                    status=status,
                    error_message=error_message,
                    data=data
                )
            except Exception:
                return ToolOutputEnvelope(
                    status="error",
                    error_message=f"Unparseable content: {raw_content}",
                    data=None
                )

    else:
        return ToolOutputEnvelope(
            status="error",
            error_message=f"Unsupported content type: {type(raw_content)}",
            data=None
        )