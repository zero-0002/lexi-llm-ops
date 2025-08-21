# Simple OpenAI Chat API with Motia

This is a simple chat API built with Motia framework that integrates with OpenAI's GPT models.

## Features

- **POST /chat**: Send a chat message and get async processing
- **GET /chat/{trace_id}/response**: Retrieve the AI response by trace ID
- Supports different OpenAI models (gpt-3.5-turbo, gpt-4, etc.)
- Adjustable temperature for response creativity
- Error handling and logging
- State management for response retrieval

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run in development mode:**
   ```bash
   npm run dev
   ```

## API Usage

### Send Chat Message

```bash
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
  }'
```

Response:
```json
{
  "traceId": "abc123-def456-ghi789",
  "message": "Chat request received and is being processed",
  "status": "processing"
}
```

### Get Chat Response

```bash
curl http://localhost:3000/chat/abc123-def456-ghi789/response
```

Response:
```json
{
  "traceId": "abc123-def456-ghi789",
  "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "status": "completed",
  "model": "gpt-3.5-turbo",
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 20,
    "total_tokens": 35
  },
  "timestamp": "2025-08-19T17:45:00Z"
}
```

## Workflow Steps

1. **ChatAPI** (`01_api_step.py`): Receives chat requests and emits to processing queue
2. **OpenAIChatProcessor** (`02_test_state_step.py`): Processes messages with OpenAI API
3. **ChatResponseHandler** (`03_check_state_change_step.py`): Handles final responses and logging
4. **GetChatResponse** (`04_get_response_api.py`): API endpoint to retrieve responses

## Parameters

- **message** (required): The user's message
- **model** (optional): OpenAI model to use (default: gpt-3.5-turbo)
- **temperature** (optional): Response creativity (0-2, default: 0.7)

## Error Handling

The API handles various error scenarios:
- Missing OpenAI API key
- Invalid request format
- OpenAI API errors
- Rate limiting
- Network issues

All errors are logged and returned with appropriate HTTP status codes.
