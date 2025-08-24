# /hierarchical_agent/schemas.py
from typing import Literal, Optional, Dict, Any, List
# from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field


class OrchestratorDecision(BaseModel):
    strategy: Literal["react", "plan_and_execute"] = Field(description="Chọn chiến lược 'react' cho các nhiệm vụ linh hoạt, hoặc 'plan_and_execute' cho các nhiệm vụ có thể lập kế hoạch trước.")
    reasoning: str = Field(description="Giải thích ngắn gọn lý do chọn chiến lược.")

class ReviewDecision(BaseModel):
    is_approved: bool = Field(description="True nếu kế hoạch được phê duyệt, False nếu bị từ chối.")
    critique: str = Field(description="Góp ý xây dựng nếu kế hoạch bị từ chối.")

class PlanStep(BaseModel):
    task_description: str = Field(description="Mô tả nhiệm vụ của bước này.")
    tool_name: str = Field(description="Tên của công cụ cần gọi.")
    parameters: Dict[str, Any] = Field(description="Các tham số cho công cụ.")

class MultiStepPlan(BaseModel):
    intent: str = Field(description="Tóm tắt mục tiêu cuối cùng của người dùng.")
    plan: List[PlanStep] = Field(description="Danh sách các bước cần thực hiện.")
    
class Task(BaseModel):
    task_id: str
    description: str
    reason: str = Field(description="Lý do vì sao tạo task này")
    # strategy: str  # "direct" | "react"
    tool: Optional[str] = None
    params: Optional[dict] = None
    depend_on: Optional[List[str]] = Field(description="Danh sách task_id mà task này phụ thuộc vào, nếu không phụ thuộc thì để []")

class PlannerOutput(BaseModel):
    tasks: List[Task]
    response: Optional[str] = Field(description="nếu visible_to_user là True tổng hợp kết quả trả về người dùng")
    visible_to_user: Optional[bool] = Field(description="Tổng hợp thông tin đẩy đủ từ các task trả lời cho người dùng, nếu task chưa hoàn thành thì trả false")

'{"tasks":[{"task_id":"1","description":"Tìm kiếm thông tin về \'Thủ tướng Việt Nam hiện tại là ai\' trên internet.","tool":"search_web","params":{"query":"Thủ tướng Việt Nam hiện tại là ai","region":"Vietnam"}},{"task_id":"2","description":"Phân tích kết quả tìm kiếm để xác định tên của Thủ tướng Việt Nam hiện tại.","tool":null,"params":null,"depend_on":["1"]}],"visible_to_user":true}'



class ToolOutputEnvelope(BaseModel):
    """
    Một cấu trúc "phong bì" chuẩn cho output của TẤT CẢ các tool.
    """
    status: Literal["success", "error"] = Field(description="Trạng thái thực thi của tool.")
    error_message: Optional[str] = Field(None, description="Thông báo lỗi nếu status là 'error'.")
    data: Any = Field(description="Dữ liệu kết quả thực tế của tool. Cấu trúc của data sẽ phụ thuộc vào từng tool cụ thể.")

# Thêm schema này vào file schemas.py của bạn


class FinalReview(BaseModel):
    """
    Cấu trúc quyết định của Reviewer cuối cùng.
    """
    is_approved: bool = Field(description="True nếu câu trả lời được duyệt, False nếu cần Planner viết lại.")
    final_answer: str = Field(description="Câu trả lời cuối cùng đã được biên tập và chau chuốt, sẵn sàng gửi cho người dùng.")
    critique: str = Field(description="Góp ý cho Planner nếu câu trả lời bị từ chối.")

