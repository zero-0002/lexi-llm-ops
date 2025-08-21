config = {
    "type": "api",
    "name": "get-chat-response",
    "path": "/api/chat/{trace_id}/response",
    "method": "GET",
    "flows": ["chat-workflow"],
    "emits": []  # No events, direct response
}

async def handler(req, context):
    params = req.get("params", {})
    trace_id = params.get("trace_id", "").strip()
    
    context.logger.info("Get Chat Response - Processing request", {
        "trace_id": trace_id,
        "request_trace_id": context.trace_id
    })
    
    # Validate trace_id
    if not trace_id:
        return {
            "status": 400,
            "body": {
                "error": "validation_error",
                "message": "Trace ID is required"
            }
        }

    try:
        # Fetch response from state
        chat_response = await context.state.get(trace_id, "chat_response")
        
        if not chat_response:
            return {
                "status": 404,
                "body": {
                    "error": "not_found",
                    "message": f"No chat response found for trace ID: {trace_id}"
                }
            }

        # Check if it's an error response
        if chat_response.get("status") == "error":
            return {
                "status": 500,
                "body": {
                    "error": "processing_error",
                    "message": chat_response.get("error", "Unknown error occurred"),
                    "traceId": trace_id,
                    "status": "error"
                }
            }

        # Return successful response
        return {
            "status": 200,
            "body": {
                "traceId": trace_id,
                "response": chat_response.get("response", ""),
                "status": chat_response.get("status", "completed"),
                "model": chat_response.get("model", ""),
                "usage": chat_response.get("usage", {}),
                "timestamp": chat_response.get("timestamp", "")
            }
        }

    except Exception as error:
        context.logger.error("Error fetching chat response", {
            "error": str(error),
            "trace_id": trace_id
        })
        
        return {
            "status": 500,
            "body": {
                "error": "internal_error",
                "message": "Failed to fetch chat response"
            }
        }
