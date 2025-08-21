import asyncio
import logging
from typing import List

# --- Các thành phần của Langchain/Langgraph ---
from langchain_core.language_models.base import BaseLanguageModel
from langchain.tools import tool, BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# --- Các thành phần của dự án ---
from agent.state import AgentState
from langchain_mcp_adapters.client import MultiServerMCPClient
from datetime import datetime

# --- Cấu hình logging ---
logger = logging.getLogger(__name__)


# --- Tool nội bộ (có thể giữ ở đây hoặc chuyển ra file riêng) ---
@tool
def get_current_time() -> str:
    """Sử dụng để lấy thời gian hiện tại của hệ thống."""
    return datetime.now().isoformat()


class AgentExecutor:
    """
    Một class quản lý việc khởi tạo và chạy một agent dựa trên LangGraph.

    Class này chịu trách nhiệm:
    1. Khởi tạo và thu thập tất cả các tools (cả nội bộ và từ MCP).
    2. "Bind" các tool này vào mô hình ngôn ngữ (LLM).
    3. Xây dựng và compile đồ thị (graph) xử lý logic của agent.
    4. Cung cấp một giao diện để thực thi agent.
    """

    def __init__(self, llm: BaseLanguageModel, mcp_client: MultiServerMCPClient):
        """
        Hàm khởi tạo.

        Args:
            llm: Một instance của mô hình ngôn ngữ (ví dụ: ChatOpenAI).
            mcp_client: Client để kết nối và lấy tool từ MCP server.
        """
        self.llm = llm
        self.mcp_client = mcp_client
        self.all_tools: List[BaseTool] = []
        self.llm_with_tools: None
        self.graph = None

    async def _initialize_tools(self):
        """
        (Async) Thu thập tất cả các tool từ các nguồn khác nhau.
        """
        # Bắt đầu với các tool nội bộ
        self.all_tools = [get_current_time]

        # Thử lấy tool từ MCP server
        try:
            mcp_tools = await self.mcp_client.get_tools()
            self.all_tools.extend(mcp_tools)
            logger.info(f"✅ Đã tải thành công {len(mcp_tools)} MCP tool(s).")
        except* Exception as eg:
            for e in eg.exceptions:
                logger.error(f"❌ Lỗi khởi tạo MCP: {repr(e)}")
            logger.warning("⚠️ Các tool MCP đã bị vô hiệu hóa vì server không sẵn sàng.")

    def _build_graph(self):
        """
        Xây dựng và compile đồ thị StateGraph.
        """
        # Bind toàn bộ tool vào LLM để planner có thể sử dụng
        self.llm_with_tools = self.llm.bind_tools(self.all_tools)

        workflow = StateGraph(AgentState)

        # Định nghĩa các node
        executor_node = ToolNode(self.all_tools)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("executor", executor_node)

        # Định nghĩa luồng công việc
        workflow.set_entry_point("planner")

        workflow.add_conditional_edges(
            "planner",
            self._should_continue,
            {
                "executor": "executor",  # Nếu cần gọi tool, đi đến executor
                END: END,               # Nếu không, kết thúc
            },
        )

        workflow.add_edge("executor", "planner")

        return workflow.compile()

    # --- Các phương thức định nghĩa Node ---

    def _planner_node(self, state: AgentState):
        """Node lập kế hoạch: Gọi LLM để quyết định hành động tiếp theo."""
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def _should_continue(self, state: AgentState) -> str:
        """Hàm quyết định luồng đi tiếp theo sau planner."""
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "executor"
        return END
    
    # --- Phương thức Factory để khởi tạo ---
    
    @classmethod
    async def create(cls, llm: BaseLanguageModel, mcp_client: MultiServerMCPClient):
        """
        Phương thức factory để khởi tạo một instance của AgentExecutor một cách an toàn,
        bao gồm cả các bước setup bất đồng bộ (async).
        """
        instance = cls(llm, mcp_client)
        await instance._initialize_tools()
        instance.graph = instance._build_graph()
        return instance

    # --- Phương thức để chạy agent ---

    async def invoke(self, inputs):
        """Thực thi agent với một đầu vào cho trước."""
        if not self.graph:
            raise ValueError("Graph chưa được khởi tạo. Hãy gọi phương thức `create`.")
        return await self.graph.ainvoke(inputs)