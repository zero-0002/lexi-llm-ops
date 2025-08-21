config = {
    "type": "api",
    "name": "chat-api",
    "path": "/api/chat",
    "method": "POST",
    "flows": ["chat-workflow"],
    "emits": [{"topic": "chat.process", "label": "Process chat message"}],
    "bodySchema": {
        "type": "object",
            "properties": {
                "message": {"type": "string","description": "hello"},
                "model": {"type": "string", "description": "gpt-4.1-nano"},
                "temperature": {"type": "number", "description": 0.7, "minimum": 0, "maximum": 2}
        },
        # "properties": {
        #     "message": {"type": "string","default": "test"},
        #     "model": {"type": "string", "default": "gpt-4.1-nano"},
        #     "temperature": {"type": "number", "default": 0.7, "minimum": 0, "maximum": 2}
        # },
        "required": ["message"]
    }
}

async def handler(req, context):
    body = req.get("body", {})
    message = body.get("message", "").strip()
    
    context.logger.info("Chat API - Processing request", {
        "message_length": len(message),
        "trace_id": context.trace_id
    })
    
    # Validate input
    if not message:
        return {
            "status": 400,
            "body": {
                "error": "validation_error", 
                "message": "Message cannot be empty"
            }
        }

    # Emit event for processing
    await context.emit({
        "topic": "chat.process",
        "data": {
            "message": message,
            "model": body.get("model", "gpt-3.5-turbo"),
            "temperature": body.get("temperature", 0.7),
            "user_trace_id": context.trace_id
        }
    })

    return {
        "status": 202,
        "body": {
            "message": "Chat request accepted",
            "traceId": context.trace_id,
            "status": "processing"
        }
    }
