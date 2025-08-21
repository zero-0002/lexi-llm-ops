from langchain.tools import tool
from datetime import datetime
import time

# Đây chỉ là ví dụ để chạy riêng lẻ, không cần thiết khi chạy bằng supervisord
# from mcp.langchain.server import run
# @tool
# def get_current_time() -> str:
#     """Sử dụng để lấy thời gian hiện tại của hệ thống."""
#     return datetime.now().isoformat()

# if __name__ == "__main__":
#     print("Starting utils server...")
#     run([get_current_time])