import streamlit as st
import requests
import time
import logging
import httpx
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API base from environment or default
API_BASE = os.getenv("BACKEND_API_URL", "http://localhost:8000") + "/api/chat"

# USER info
user_id = "tinh123"
bot_id = "botLegal"

st.set_page_config(page_title="Legal Chatbot", layout="wide")
st.title("🤖 Luật sư ảo - ChatBot Pháp Luật")

# ========== FUNCTIONS ==========

import re

def extract_tool_and_input(text):
    tool_match = re.search(r'Action:\s*\[(\w+)\]', text)
    input_match = re.search(r'Action Input:\s*\[(.*?)\]', text)

    tool = tool_match.group(1) if tool_match else None
    input_str = input_match.group(1) if input_match else None

    # Tách chuỗi input nếu là danh sách nhiều chuỗi
    if input_str:
        inputs = [s.strip().strip('"') for s in input_str.split(',')]
    else:
        inputs = []

    return tool, inputs

def re_check_final_answer(text: str):
    """
    Tìm và trích xuất nội dung sau 'Final Answer:' trong chuỗi đầu ra của LLM.
    
    Args:
        text (str): Chuỗi đầu ra từ LLM hoặc quá trình stream.

    Returns:
        Optional[str]: Nội dung sau 'Final Answer:' nếu tìm thấy, ngược lại trả về None.
    """
    match = re.search(r"Final Answer:\s*(.*)", text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def fetch_conversations():
    res = requests.get(f"{API_BASE}/conversations", params={"user_id": user_id})
    if res.status_code == 200:
        return res.json()
    return []

def fetch_messages(conversation_id):
    res = requests.get(f"{API_BASE}/messages", params={"conversation_id": conversation_id})
    if res.status_code == 200:
        return res.json()
    return []

def send_user_message(message, conversation_id=None):
    payload = {
        "user_id": user_id,
        "message": message
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    res = requests.post(f"{API_BASE}/send", json=payload)
    if res.status_code == 200:
        return res.json()
    return None

def trigger_generate(query, conv_id: str):

    payload = {
        "rewrite_query": query,
        "use_web_search": True,
        "user_id": user_id,
        "conversation_id": conv_id
    }
    return requests.post(
        API_BASE + "/generate_response",
        json=payload
    )

def trigger_web_search(query_web_search: str):
    payload = {
        "query": query_web_search,
    }
    return requests.post("http://localhost:8000/api/rag/web_search", json=payload)

def analyze_query(query: str):
    return requests.post(
        API_BASE + "/query/analyze",
        json={"query": query}
    ).json()

def stream_analyze_query(conversation_id: str, user_id: str, query: str):
    with requests.post(
        API_BASE + "/query/analyze", 
        json={
            "conversation_id": conversation_id,
            "user_id": user_id,
            "query": query
        },
        stream=True
    ) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


def delete_conversation(conversation_id):
    res = requests.delete(f"{API_BASE}/conversations", params={
        "user_id": user_id,
        "conversation_id": conversation_id
    })
    return res.status_code == 200
\
# ========== SIDEBAR ==========

st.sidebar.title("💬 Các cuộc hội thoại")

# Nút tạo cuộc trò chuyện mới
if st.sidebar.button("➕ Tạo cuộc trò chuyện mới"):
    st.session_state.conversation_id = None
    st.session_state.messages = []

# Lấy danh sách các cuộc hội thoại
conversations = fetch_conversations()
for conv in conversations:
    col1, col2 = st.sidebar.columns([5, 1])
    label = f"🗂 {conv['conversation_id'][:8]}... ({conv.get('message_count', 0)})"
    if col1.button(label, key=conv["conversation_id"]):
        st.session_state.conversation_id = conv["conversation_id"]
        st.session_state.messages = fetch_messages(conv["conversation_id"])
    if col2.button("🗑️", key=f"del_{conv['conversation_id']}"):
        success = delete_conversation(conv["conversation_id"])
        if success:
            st.success("Đã xoá cuộc hội thoại")
            if st.session_state.get("conversation_id") == conv["conversation_id"]:
                st.session_state.conversation_id = None
                st.session_state.messages = []
            st.rerun()

# ========== MESSAGE DISPLAY ==========

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

st.divider()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])

# ========== INPUT AREA ==========

if user_input := st.chat_input("Nhập câu hỏi..."):
    # ✅ Hiển thị luôn input của user
    st.session_state.messages.append({
        "role": "user",
        "text": user_input,
        "created_at": ""
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Gửi lên server
    response = send_user_message(user_input, st.session_state.conversation_id)

    if not response:
        st.error("❌ Gửi câu hỏi thất bại!")
        st.stop()

    # Cập nhật conversation_id nếu cần
    st.session_state.conversation_id = response["conversation_id"]

    # Nếu có reuse → hiển thị ngay
    if response.get("status") == "reused" and response.get("answer"):
        with st.chat_message("assistant"):
            st.markdown(response["answer"])
        st.session_state.messages.append({
            "role": "assistant",
            "text": response["answer"],
            "created_at": "",
        })
        st.stop()

    # Nếu không reuse → tiếp tục phân tích
    with st.chat_message("assistant"):
        msg_box = st.empty()
        msg_box.markdown("💬 Đang phân tích truy vấn...")

        collected = ""
        try:
            for chunk in stream_analyze_query(st.session_state.conversation_id, user_id, user_input):
                collected += chunk
                html_text = collected.replace("\n", "<br>")
                msg_box.markdown(html_text, unsafe_allow_html=True)
        except Exception as e:
            msg_box.markdown("❌ Lỗi khi gọi API: " + str(e))
            st.stop()

        # ✅ Lưu assistant response vào session
        st.session_state.messages.append({
            "role": "assistant",
            "text": collected,
            "created_at": ""
        })
        if re_check_final_answer(collected):
            st.stop()
        tool, inputs = extract_tool_and_input(collected)
        if tool == "web_search":
            msg_box.markdown(f"{collected} \n🌐 Đang tìm kiếm thêm thông tin web...")
            result = trigger_web_search(inputs[0]).json()
            if result.get("results"):
                urls = [r["url"] for r in result["results"]['results']]
            else:
                urls = []
            urls = "  \n".join(urls) if urls else "Không tìm thấy kết quả nào."
            collected += f"  \n🌐 Kết quả tìm kiếm từ web: {urls}  \n✅Đang tổng hợp kết quả...  \n"
            msg_box.markdown(collected)
        else:
            st.stop()
        trigger_generate(user_input, st.session_state.conversation_id)
        # conv_id = "4a5d959f-dd7a-4815-9147-f8dba203f115"
        conv_id = st.session_state.conversation_id
        url = f"http://localhost:8000/api/chat/stream_answer/?conv_id={conv_id}"

        with requests.get(url, stream=True, timeout=30) as r:
            for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    collected += chunk
                    if "[END]" in chunk:
                        break
                    # html_text = collected.replace("\n", "<br>")
                    msg_box.markdown(collected, unsafe_allow_html=True)
        # else:
        #     msg_box.markdown("⚠️ Hệ thống đang xử lý chậm. Vui lòng kiểm tra lại sau.")
