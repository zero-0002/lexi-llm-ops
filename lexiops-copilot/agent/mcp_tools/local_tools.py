from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from langchain.tools import tool
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from typing import Optional
from pydantic import BaseModel, Field
from typing import Literal
from agent.schemas import ToolOutputEnvelope

@tool
def get_current_time() -> ToolOutputEnvelope:
    """Sử dụng để lấy thời gian hiện tại của hệ thống."""
    try:
        data = datetime.now().isoformat()
        return ToolOutputEnvelope(
            status="success",
            data=data
        )
    except Exception as e:
        return ToolOutputEnvelope(
            status="error",
            error_message=str(e)
        )


class WebSearchInput(BaseModel):
    query: str = Field(..., description="Truy vấn tìm kiếm")
    region: Literal["wt-wt", "us-en", "vn-vi", "jp-jp"] = Field(
        "us-en", 
        description="Mã vùng DuckDuckGo. Giá trị cho phép: 'wt-wt' (WorldWide), 'us-en' (Mỹ), 'vn-vi' (Việt Nam), 'jp-jp' (Nhật Bản)"
    )
    max_results: int = Field(3, description="Số lượng kết quả tối đa ưu tiên là 3")

@tool(args_schema=WebSearchInput)
def search_web(query: str, region: str, max_results: int = 3) -> ToolOutputEnvelope:
    """
   "Tìm kiếm thông tin trên web dựa trên từ khóa `query` và khu vực `region`. "
    "Sử dụng để lấy dữ liệu cập nhật, tin tức hoặc thông tin tổng quan từ Internet. "
    "Thích hợp khi cần trích xuất thông tin nhanh và chính xác từ nhiều nguồn."
    "Trả về list dict [{{title, url, snippet, body}}, ...]"
    """
    results_data = []
    print(f"--- Đang tìm '{query}' (region={region}) ---")

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, region=region, max_results=max_results)
    except Exception as e:
        return [{"error": f"Lỗi khi gọi DuckDuckGo: {e}"}]

    if not results:
        return [{"error": "Không tìm thấy kết quả."}]

    for r in results:
        title = r.get("title") or ""
        snippet = r.get("snippet") or ""
        url = r.get("href") or None
        body_text = ""

        if url:
            try:
                resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                body_text = soup.get_text(separator="\n", strip=True)
            except Exception as e:
                body_text = f"[Fetch error: {e}]"

        results_data.append({
            "title": title,
            "snippet": snippet,
            "body": body_text[:2500]
        })
    if len(results_data) == 0:
        return ToolOutputEnvelope(
            status="error",
            error_message="Không tìm thấy kết quả."
        )
    return ToolOutputEnvelope(
        status="success",
        data=results_data
    )

@tool
def get_current_weather(city: str) -> ToolOutputEnvelope:
    """Lấy thông tin thời tiết hiện tại cho một thành phố cụ thể."""
    print(f"--- Lấy thời tiết cho thành phố: '{city}' ---")
    if city.lower() == "hồ chí minh":
        return ToolOutputEnvelope(
            status="success",
            data="Thời tiết tại TP. Hồ Chí Minh hiện tại là 32°C, trời nắng."
        )
    return ToolOutputEnvelope(
        status="error",
        error_message=f"Không có dữ liệu thời tiết cho {city}."
    )
