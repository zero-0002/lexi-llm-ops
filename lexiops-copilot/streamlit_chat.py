import streamlit as st
import requests
import json
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="LexiOps Copilot Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/lexiops/copilot',
        'Report a bug': "https://github.com/lexiops/copilot/issues",
        'About': "# LexiOps Copilot Chat\nKubernetes Operations Assistant with AI"
    }
)

# Custom CSS - Simple colors for both light and dark themes
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4f46e5;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.75rem 0;
        border: 2px solid;
    }
    
    .user-message {
        background-color: #dbeafe;
        border-color: #3b82f6;
        color: #1e40af;
    }
    
    .assistant-message {
        background-color: #dcfce7;
        border-color: #22c55e;
        color: #166534;
    }
    
    .tool-result {
        background-color: #fef3c7;
        border: 2px solid #f59e0b;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.75rem 0;
        font-family: monospace;
        font-size: 0.9rem;
        color: #92400e;
    }
    
    .tool-result pre {
        color: #374151;
        background-color: #f9fafb;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border: 1px solid #d1d5db;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.6rem;
        border-radius: 0.5rem;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 0.5rem;
        color: white;
    }
    
    .status-success {
        background-color: #10b981;
    }
    
    .status-error {
        background-color: #ef4444;
    }
    
    .status-warning {
        background-color: #f59e0b;
    }
    
    /* Dark theme overrides */
    .stApp[data-theme="dark"] .user-message {
        background-color: #1e3a8a;
        border-color: #60a5fa;
        color: #bfdbfe;
    }
    
    .stApp[data-theme="dark"] .assistant-message {
        background-color: #166534;
        border-color: #4ade80;
        color: #bbf7d0;
    }
    
    .stApp[data-theme="dark"] .tool-result {
        background-color: #92400e;
        border-color: #fbbf24;
        color: #fde68a;
    }
    
    .stApp[data-theme="dark"] .tool-result pre {
        background-color: #374151;
        border-color: #6b7280;
        color: #f3f4f6;
    }
    
    .stApp[data-theme="dark"] .main-header {
        color: #818cf8;
    }
    
    /* Simple button styling */
    .stButton > button {
        background-color: #f3f4f6;
        color: #374151;
        border: 2px solid #d1d5db;
        border-radius: 0.5rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #e5e7eb;
        border-color: #9ca3af;
    }
    
    .stApp[data-theme="dark"] .stButton > button {
        background-color: #374151;
        color: #f9fafb;
        border-color: #6b7280;
    }
    
    .stApp[data-theme="dark"] .stButton > button:hover {
        background-color: #4b5563;
        border-color: #9ca3af;
    }
    
    /* Simple animations */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-message {
        animation: slideIn 0.3s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8001/chat"

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # API URL
    api_url = st.text_input(
        "API URL",
        value=st.session_state.api_url,
        help="FastAPI chat endpoint"
    )
    st.session_state.api_url = api_url
    
    # Test connection
    if st.button("🔍 Test Connection"):
        try:
            response = requests.get(api_url.replace("/chat", "/health"), timeout=5)
            if response.status_code == 200:
                st.success("✅ Connection successful!")
            else:
                st.error(f"❌ Connection failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")
    
    st.divider()
    
    # Quick commands
    st.subheader("🚀 Quick Commands")
    quick_commands = [
        "List all pods",
        "Get services in lexiops-copilot namespace",
        "Show deployment status",
        "Get pod logs",
        "Check cluster nodes",
        "Show recent events",
        "What time is it?",
        "Create nginx deployment"
    ]
    
    for cmd in quick_commands:
        if st.button(cmd, key=f"quick_{cmd}"):
            # Add user message
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({
                "role": "user", 
                "content": cmd,
                "timestamp": timestamp
            })
            
            # Call API for quick command
            with st.spinner("🤖 Processing quick command..."):
                try:
                    response = requests.post(
                        st.session_state.api_url,
                        json={"message": cmd},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        assistant_content = result.get("response", "No response received")
                        tool_results = result.get("tool_results", [])
                        
                        # Add assistant message
                        assistant_msg = {
                            "role": "assistant",
                            "content": assistant_content,
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        }
                        
                        if tool_results:
                            assistant_msg["tool_results"] = tool_results
                        
                        st.session_state.messages.append(assistant_msg)
                        
                    else:
                        error_msg = f"API Error: {response.status_code}"
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"❌ {error_msg}",
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        })
                        
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ Error: {str(e)}",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
            
            st.rerun()
    
    st.divider()
    
    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    # Stats
    st.subheader("📊 Stats")
    st.metric("Messages", len(st.session_state.messages))
    if st.session_state.messages:
        last_msg_time = st.session_state.messages[-1].get("timestamp", "N/A")
        st.metric("Last Message", last_msg_time)

# Main chat interface
st.markdown('<h1 class="main-header">🤖 LexiOps Copilot Chat</h1>', unsafe_allow_html=True)

# Chat container
chat_container = st.container()

# Auto-scroll to bottom function
def scroll_to_bottom():
    st.markdown("""
    <script>
        var element = window.parent.document.querySelector('.main .block-container');
        element.scrollTop = element.scrollHeight;
    </script>
    """, unsafe_allow_html=True)

with chat_container:
    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp", "")
        
        if role == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 You</strong> 
                <span style="float: right; font-size: 0.8em;">{timestamp}</span><br>
                <div style="margin-top: 0.5rem;">{content}</div>
            </div>
            """, unsafe_allow_html=True)
        
        elif role == "assistant":
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 LexiOps Copilot</strong> 
                <span style="float: right; font-size: 0.8em;">{timestamp}</span><br>
                <div style="margin-top: 0.5rem;">{content}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show tool results if available
            if "tool_results" in message:
                st.markdown("**🔧 Tool Results:**")
                for j, tool in enumerate(message["tool_results"]):
                    tool_name = tool.get("name", "Unknown")
                    tool_content = tool.get("content", "")
                    
                    # Determine status
                    if "Error:" in str(tool_content):
                        status_class = "status-error"
                        status_text = "ERROR"
                    elif "SUCCESS" in str(tool_content) or tool_content:
                        status_class = "status-success"
                        status_text = "SUCCESS"
                    else:
                        status_class = "status-warning"
                        status_text = "WARNING"
                    
                    # Truncate long content
                    display_content = str(tool_content)
                    if len(display_content) > 500:
                        display_content = display_content[:500] + "\n... (xem thêm)"
                    
                    st.markdown(f"""
                    <div class="tool-result">
                        <span class="status-badge {status_class}">{status_text}</span>
                        <strong>{tool_name}</strong><br>
                        <pre>{display_content}</pre>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Simple spacing for messages
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "timestamp": timestamp
    })
    
    # Call API
    with st.spinner("🤖 LexiOps Copilot is thinking..."):
        try:
            response = requests.post(
                st.session_state.api_url,
                json={"message": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_content = result.get("response", "No response received")
                tool_results = result.get("tool_results", [])
                
                # Add assistant message
                assistant_msg = {
                    "role": "assistant",
                    "content": assistant_content,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                
                if tool_results:
                    assistant_msg["tool_results"] = tool_results
                
                st.session_state.messages.append(assistant_msg)
                
            else:
                error_msg = f"API Error: {response.status_code} - {response.text[:200]}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ {error_msg}",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                
        except requests.exceptions.Timeout:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "⏱️ Request timed out. Please try again.",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Error: {str(e)}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
    
    # Rerun to show the new messages
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 0.9rem; padding: 1rem 0;">
    🚀 <strong>LexiOps Copilot</strong> - Kubernetes Operations Assistant<br>
    <small>Powered by FastAPI + LangGraph + MCP Tools</small>
</div>
""", unsafe_allow_html=True)
