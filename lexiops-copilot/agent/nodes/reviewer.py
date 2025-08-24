# /nodes/final_reviewer.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from ..state import AgentState
from agent.schemas import FinalReview
# Giả sử bạn có file prompts.py
# from ..prompts import FINAL_REVIEWER_PROMPT 

# Bạn có thể đặt prompt này trong file prompts.py
FINAL_REVIEWER_PROMPT = """Bạn là một Biên tập viên AI chuyên nghiệp và cực kỳ khó tính. 
Nhiệm vụ của bạn là xem xét câu trả lời dự thảo do một AI khác tạo ra và đảm bảo nó đạt chất lượng cao nhất trước khi gửi cho người dùng.

**Yêu cầu ban đầu của người dùng:**
{original_query}

**Câu trả lời dự thảo từ Planner:**
{draft_answer}

**Hãy thực hiện các bước sau:**
1.  **Đánh giá:** Xem xét câu trả lời dự thảo dựa trên các tiêu chí:
    - Có giải quyết đúng và đủ yêu cầu ban đầu không?
    - Thông tin có chính xác không?
    - Văn phong có tự nhiên, lịch sự, và chuyên nghiệp không?
    - Có dễ đọc và rõ ràng không?

2.  **Quyết định:**
    - **Câu trả lời phải trả lời được yếu cầu không đợi thực thi
    - **Không approved những câu trả lời đang thực thi
    - **Nếu câu trả lời về cơ bản là tốt:** Hãy chỉnh sửa lại một chút về ngữ pháp, từ ngữ để nó trở nên hoàn hảo. Sau đó, đặt `is_approved` thành `True`.
    - **Nếu câu trả lời có vấn đề nghiêm trọng (sai thông tin, không liên quan, diễn đạt kém):** Đừng cố sửa nó. Hãy viết một lời góp ý (critique) ngắn gọn, rõ ràng để Planner có thể làm lại. Sau đó, đặt `is_approved` thành `False`.

Output của bạn phải là một đối tượng JSON hợp lệ."""

class ReviewerNode:
    def __init__(self, llm):
        # Tạo chain sẽ trả về đối tượng Pydantic FinalReview
        self.chain = (
            ChatPromptTemplate.from_template(FINAL_REVIEWER_PROMPT)
            | llm.with_structured_output(FinalReview)
        )

    def __call__(self, state: AgentState) -> dict:
        print("--- NODE: FINAL REVIEWER/RESPONDER ---")
        
        # Lấy yêu cầu gốc của người dùng (thường là tin nhắn đầu tiên)
        original_query = state["messages"][0].content
        # Lấy câu trả lời dự thảo từ Planner (thường là tin nhắn cuối cùng)
        draft_answer = state["messages"][-1].content

        # Gọi LLM để thực hiện review
        review_result: FinalReview = self.chain.invoke({
            "original_query": original_query,
            "draft_answer": draft_answer
        })

        # Dựa trên quyết định của review để cập nhật state
        if review_result.is_approved:
            print(f"--- Reviewer: [PASS] - Câu trả lời cuối cùng: {review_result.final_answer} ---")
            
            # Tạo tin nhắn cuối cùng để trả lời người dùng
            final_message_to_user = AIMessage(content=review_result.final_answer)
            
            # Trả về tin nhắn này và một cờ để định tuyến đến END
            return {
                "messages": [final_message_to_user],
                "review_outcome": "approved"
            }
        else:
            print(f"--- Reviewer: [FAIL] - Góp ý: {review_result.critique} ---")
            
            # Tạo tin nhắn feedback để gửi lại cho Planner
            feedback_message = HumanMessage(content=f"[Phản hồi từ Reviewer] chưa có kết quả visible_to_user phải là False: {review_result.critique}")

            # Trả về tin nhắn feedback và một cờ để định tuyến quay lại Planner
            return {
                "messages": [feedback_message],
                "review_outcome": "rejected"
            }