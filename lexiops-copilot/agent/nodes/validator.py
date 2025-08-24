from agent.state import AgentState
from langgraph.graph import StateGraph, END
import logging
from langchain_core.messages import HumanMessage, AIMessage
import json
from pydantic import ValidationError
from agent.schemas import PlannerOutput
logging.basicConfig(level=logging.DEBUG)

from langchain_core.messages import HumanMessage
from ..state import AgentState

class ValidatorNode:
    """
    Node Validator chịu trách nhiệm:
    1. Kiểm tra lỗi parsing từ Planner.
    2. Nếu parsing thành công, kiểm tra logic của kế hoạch.
    3. Cập nhật state['messages'] và cờ 'is_approved' để định tuyến.
    """
    def __init__(self, llm, tools):
        # Có thể khởi tạo một chain riêng cho việc review logic nếu cần
        # self.review_logic_chain = ...
        pass

    def __call__(self, state: AgentState) -> dict:
        print("--- NODE: VALIDATOR ---")
        planner_output = state.get("planner_output")
        # --- Cấp 1: Kiểm tra lỗi Parsing ---
        if planner_output.get("parsing_error"):
            print("--- Validator: [FAIL] - Phát hiện lỗi parsing từ Planner ---")
            
            # error = planner_output["parsing_error"]
            
            tool_calls = planner_output.get("raw").additional_kwargs.get("tool_calls", [])
            if len(tool_calls) > 0:
                arguments_str = tool_calls[0]["function"]["arguments"]
            raw_ai_message = AIMessage(content=arguments_str)
            error = validate_planner_output(arguments_str)
            # Tạo tin nhắn phản hồi để Planner tự sửa lỗi
            feedback_message = HumanMessage(
                content=f"Output của bạn không hợp lệ và không thể parse. Hãy kiểm tra lại các parameters, cấu trúc file json và sửa lại.\n"
                        # f"Lỗi parsing: {error}\n"
                        f"Các lỗi chi tiết:" + "\n".join(error)
            )
            # Quay lại Planner với tin nhắn lỗi
            current_scratchpad = state.get('scratchpad', [])

            # Tạo các tin nhắn mới cho vòng lặp sửa lỗi
            new_scratchpad_content = current_scratchpad + [raw_ai_message, feedback_message]
            return { "scratchpad": new_scratchpad_content, "is_valid": False}

        # --- Cấp 2: Kiểm tra Logic của Kế hoạch ---
        else:
            print("--- Validator: Parsing thành công, đang kiểm tra logic... ---")
            parsed_plan = planner_output.get("parsed")
            
            raw_ai_message = planner_output.get("raw").additional_kwargs.get("tool_calls", [])
            if len(raw_ai_message) > 0:
                arguments_str = raw_ai_message[0]["function"]["arguments"]
            raw_ai_message = AIMessage(content=arguments_str)
            # TODO: Thêm logic kiểm tra nghiệp vụ phức tạp ở đây.
            # Ví dụ: kiểm tra xem tool có tồn tại không, các task có bị lặp không, v.v.
            # Ở đây, chúng ta tạm thời mặc định là logic luôn đúng.
            if parsed_plan.visible_to_user:
                return {
                    "messages": [raw_ai_message],
                    "scratchpad": [],
                    "is_valid": True, 
                    "is_approved": True,
                    "plan": parsed_plan
                }
            
            print("--- Validator: [PASS] - Kế hoạch hợp lệ. ---")
            return {
                "messages": [raw_ai_message], 
                "scratchpad": [],
                "is_valid": True, 
                "plan": parsed_plan
            }
            
def validate_planner_output(raw_content: str):
    """
    Validate planner output against PlannerOutput schema.
    Return (parsed_output, list_of_errors).
    """
    errors = []

    # 1. Parse JSON string
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        errors.append(f"Lỗi JSON: {str(e)}. Hãy trả về một JSON hợp lệ theo schema PlannerOutput.")
        return errors  # không parse được thì return sớm

    # 2. Validate schema bằng Pydantic
    try:
        parsed = PlannerOutput(**data)
    except ValidationError as e:
        # Gom tất cả validation errors của Pydantic
        for err in e.errors():
            loc = ".".join(map(str, err["loc"]))
            msg = err["msg"]
            errors.append(f"Lỗi schema tại '{loc}': {msg}")
        return errors

    # 3. Check logic các field trong từng Task
    for idx, task in enumerate(parsed.tasks):
        if not task.task_id:
            errors.append(f"Task[{idx}] thiếu field 'task_id'.")
        if not task.description:
            errors.append(f"Task[{idx}] thiếu field 'description'.")
        elif not isinstance(task.depend_on, list):
            errors.append(f"Task[{idx}] 'depend_on' phải là list.")

    return  errors