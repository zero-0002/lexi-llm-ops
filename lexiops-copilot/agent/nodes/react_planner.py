from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from agent.state import AgentState
from agent.schemas import PlannerOutput
#     - Mỗi task bắt buộc phải có các trường (task_id, description, reason, depend_on).
planner_prompt = """
     Bạn là Planner Agent. 
    Nhiệm vụ: phân tích yêu cầu người dùng và tạo kế hoạch dưới dạng các task để thực hiện.
    Yêu cầu:
    - Chia nhỏ yêu cầu thành các task cụ thể, rõ ràng, có thể thực hiện được qua tool.
    - Mỗi task bắt buộc phải có các trường (task_id, description, reason, depend_on).
    - Hạn chế tạo task dư thừa, chỉ tạo số lượng task tối thiểu để hoàn thành yêu cầu.
    - Nếu task cần gọi tool → chỉ định tool và params.
    - Các task không phụ thuộc là các task phải sửa dụng tool sẽ thực hiện bởi AI executor.
    - Nếu có thể giải quyết bằng shell command trực tiếp thì ưu tiên tool functions.execute_shell_command.
    - Nếu task cần tìm kiếm thông tin từ web → sử dụng tool đã cung cấp.
    - task_id phải đánh số "1", "2", "3"... thay vì "task_1".
    - depend_on: danh sách task_id phụ thuộc, nếu không phụ thuộc → để [].
    Dưới đây là các công cụ có sẵn bạn có thể dùng:
    {tool_definitions}
"""

class PlannerNode:
    def __init__(self, llm, tools):
        tool_definitions = "\n".join([f"- {t.name}: {t.description}" for t in tools])
        
        # Tạo prompt với MessagesPlaceholder
        # System prompt vẫn giữ vai trò chỉ dẫn chung
        # MessagesPlaceholder sẽ là nơi chèn toàn bộ lịch sử hội thoại
        prompt = ChatPromptTemplate.from_messages([
            ("system", planner_prompt.format(tool_definitions=tool_definitions)),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        # Chain vẫn giữ nguyên, nhưng bây giờ nó nhận vào biến "messages"
        self.chain = prompt | llm.with_structured_output(PlannerOutput, include_raw=True,method="function_calling")

    def __call__(self, state: AgentState) -> dict:
        print("--- NODE: REACT PLANNER (với đầy đủ ngữ cảnh) ---")
        
        # Lấy TOÀN BỘ danh sách messages từ state
        messages = state.get('messages', [])

        # Lấy vùng nháp chứa các lỗi và feedback
        scratchpad = state.get('scratchpad', [])

        # Kết hợp cả hai để có ngữ cảnh đầy đủ nhất cho LLM
        # LLM sẽ thấy cả tiến trình đúng và lỗi sai cần sửa
        full_context = messages + scratchpad

        # Truyền toàn bộ lịch sử vào chain
        # Framework sẽ tự động định dạng danh sách này một cách chính xác cho LLM
        response_dict = self.chain.invoke({"messages": full_context})
        
        # Giả sử schema của bạn là PlannerOutput và bạn dùng include_raw=True
        # response_dict sẽ là: {"raw": AIMessage(...), "parsed": PlannerOutput(...)}
        # Chúng ta chỉ cần tin nhắn thô để thêm lại vào state
        # raw_ai_message = response_dict["raw"]

        # Trả về AIMessage thô để duy trì lịch sử một cách nhất quán
        return {"planner_output": response_dict}
