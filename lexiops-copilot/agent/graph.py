from langgraph.graph import StateGraph, END
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
)

# Import logging config FIRST để tắt debug logs
from agent.utils.logging_config import suppress_debug_logs

# --- Các thành phần của dự án ---
from agent.state import AgentState
from agent.nodes.react_planner import PlannerNode
from agent.nodes.validator import ValidatorNode
from agent.nodes.executor import ExecutorNode
from agent.nodes.reviewer import ReviewerNode
# --- Cấu hình logging ---
# logger = logging.getLogger(__name__)



# Định nghĩa cho TOÀN BỘ KẾ HOẠCH mà Planner trả về
class HierarchicalAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Khởi tạo các node từ class
        planner = PlannerNode(self.llm, self.tools)
        # orchestrator = OrchestratorNode(self.llm)
        # react_planner = ReActPlannerNode(self.llm, self.tools)
        # react_reviewer = ReActReviewerNode(self.llm, self.tools)
        # ... khởi tạo các node còn lại
        validator = ValidatorNode(self.llm, self.tools)
        executor = ExecutorNode(self.llm, self.tools)
        reviewer = ReviewerNode(self.llm)
        # --- Giả lập các node còn lại để đơn giản hóa ví dụ ---

        # --- Thêm node vào graph ---
        workflow.add_node("planner", planner)
        workflow.add_node("validate_output", validator)
        workflow.add_node("executor", executor)
        workflow.add_node("reviewer", reviewer)  # Node kết thúc
        # workflow.add_node("react_planner", react_planner_node) # Thay bằng instance của node class
        # workflow.add_node("plan_execute_planner", plan_execute_planner_node) # Thay bằng instance của node class
        # ... thêm các node reviewer, executor, responder

        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "validate_output")

        def _router_validate_output(state: AgentState) -> str:
            if state.get("is_valid"):
                if state.get("is_approved"):
                    return "reviewer"
                else:
                    return "executor"
            return "planner"

        workflow.add_conditional_edges(
            "validate_output",
            _router_validate_output,
            {
                "planner": "planner",
                "executor": "executor",
                "reviewer": "reviewer"
            }
        )
        workflow.add_edge("executor", "planner")
        
        def _router_reviewer(state: AgentState) -> str:
            if state.get("review_outcome") == "approved":
                return END
            return "planner"
        
        workflow.add_conditional_edges("reviewer", _router_reviewer,{
            "planner": "planner",
            END: END
        })
        # Từ đây, bạn sẽ xây dựng các luồng con cho ReAct và Plan-and-Execute
        # Ví dụ:
        # workflow.add_edge("planner", END)
        # workflow.add_edge("plan_execute_planner", END)

        return workflow.compile()

    async def astream(self, query: str):
        """
        Giao diện bất đồng bộ để stream các bước thực thi của agent.
        Đây là một async generator.
        """
        initial_state = {"messages": [HumanMessage(content=query)]}
        
        # Dùng 'async for' để lặp qua từng sự kiện trong luồng
        # và 'yield' nó ra cho người gọi.
        async for event in self.graph.astream(initial_state):
            yield event