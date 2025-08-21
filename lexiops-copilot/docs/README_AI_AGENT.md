# LexiOps Copilot AI Agent with GPT-4 Turbo

## Tính năng mới

✅ **AI-Powered Planning**: Sử dụng GPT-4 Turbo để tạo kế hoạch thông minh  
✅ **Intelligent Synthesis**: Response tự nhiên và thông minh từ AI  
✅ **Fallback Mechanism**: Vẫn hoạt động khi không có OpenAI API  
✅ **MCP Integration**: Kết hợp với MCP tools  

## Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup OpenAI API Key
```bash
# Copy template
cp .env.example .env

# Edit .env and add your API key
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Khởi chạy agent
```bash
# Option 1: Use script
./run_ai_agent.sh

# Option 2: Manual
uvicorn agent.main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing

### Quick test
```bash
# Single query test
python test_ai_agent.py "What time is it and what can you do?"

# Full test suite  
python test_ai_agent.py
```

### API test với curl
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze the current system and tell me what you can do"}'
```

## Workflow Architecture

```
User Input 
    ↓
🧠 PLANNER NODE (GPT-4 Turbo)
    ├─ Intelligent task analysis
    ├─ Smart tool selection  
    └─ Creates execution plan
    ↓
🔧 EXECUTOR NODE (MCP Tools)
    ├─ get_current_time
    ├─ get_system_info
    └─ filesystem_read_file
    ↓
💬 SYNTHESIZER NODE (GPT-4 Turbo) 
    ├─ Natural language generation
    ├─ Context-aware responses
    └─ User-friendly output
```

## Example Interactions

**Time Request:**
```
User: "What time is it?"
AI: "The current time is 2025-08-20 11:23:45. Is there anything else I can help you with?"
```

**System Analysis:**
```
User: "Tell me about this system"
AI: "I can see you're running on a Windows system. The current working directory is D:/Data/Legal-Retrieval/lexiops-copilot. I have access to several tools including file reading, time checking, and system information gathering. What specific information would you like to know?"
```

**File Operations:**
```
User: "Can you read the README file?"
AI: "I'd be happy to read a README file for you. I can access the filesystem and read files. Let me check what's available..."
```

## Node Details

### Planner Node
- **Model**: GPT-4 Turbo (gpt-4-1106-preview)
- **Temperature**: 0.1 (focused, consistent)
- **Function**: Intelligent task analysis và tool selection
- **Fallback**: Rule-based planning if AI fails

### Synthesizer Node  
- **Model**: GPT-4 Turbo (gpt-4-1106-preview)
- **Temperature**: 0.3 (creative, natural)
- **Function**: Convert tool results into natural responses
- **Fallback**: Template-based responses if AI fails

## Troubleshooting

### Common Issues

1. **OpenAI API Error**
   ```
   Solution: Check your API key in .env file
   Fallback: Agent uses rule-based planning
   ```

2. **MCP Tools Not Loading**
   ```
   Solution: Check MCP server is running
   Fallback: Uses built-in tools only
   ```

3. **Import Errors**
   ```
   Solution: pip install -r requirements.txt
   ```

## API Endpoints

- `GET /` - Root endpoint with usage info
- `GET /health` - Health check  
- `POST /chat` - Main chat interface
- `GET /docs` - Auto-generated API documentation
