config = {
    "type": "event",
    "name": "chat-response-handler",
    "flows": ["chat-workflow"],
    "subscribes": ["chat.response"],
    "emits": [],  # Final step, no further emissions
    "input": None
}

async def handler(input, context):
    context.logger.info("Chat Response Handler - Processing", {
        "trace_id": context.trace_id,
        "status": input.get("status", "unknown")
    })

    user_trace_id = input.get("user_trace_id")
    if not user_trace_id:
        context.logger.error("Chat Response Handler - Missing user_trace_id", {
            "trace_id": context.trace_id,
            "input_data": input
        })
        return

    try:
        # Store the response in state using the original user trace_id
        await context.state.set(user_trace_id, "chat_response", {
            "response": input.get("response", ""),
            "model": input.get("model", ""),
            "usage": input.get("usage", {}),
            "status": input.get("status", "completed"),
            "error": input.get("error", ""),
        })

        context.logger.info("Chat Response Handler - Stored successfully", {
            "trace_id": context.trace_id,
            "user_trace_id": user_trace_id,
            "response_length": len(input.get("response", "")),
            "status": input.get("status", "completed")
        })

    except Exception as error:
        context.logger.error("Chat Response Handler - Storage error", {
            "trace_id": context.trace_id,
            "user_trace_id": user_trace_id,
            "error": str(error)
        })

        # Store error state
        try:
            await context.state.set(user_trace_id, "chat_response", {
                "response": "",
                "error": f"Storage error: {str(error)}",
                "status": "error",
            })
        except Exception as storage_error:
            context.logger.error("Chat Response Handler - Critical storage failure", {
                "trace_id": context.trace_id,
                "user_trace_id": user_trace_id,
                "storage_error": str(storage_error)
            })
