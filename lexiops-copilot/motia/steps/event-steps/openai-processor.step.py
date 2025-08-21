import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

config = {
    "type": "event",
    "name": "openai-chat-processor",
    "flows": ["chat-workflow"],
    "subscribes": ["chat.process"],
    "emits": [{"topic": "chat.response", "label": "Chat response ready"}],
    "input": None  
}

async def handler(input, context):
    context.logger.info("OpenAI Chat Processor - Starting", {
        "trace_id": context.trace_id,
        "message_length": len(input.get("message", ""))
    })

    message = input.get("message", "hello")
    model = input.get("model", "gpt-4.1-nano")
    temperature = input.get("temperature", 0.7)
    user_trace_id = input.get("user_trace_id")

    try:
        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if not client.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        # Call OpenAI API
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ],
            temperature=temperature
        )

        # Extract response content
        content = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        context.logger.info("OpenAI Chat Processor - Success", {
            "trace_id": context.trace_id,
            "model": model,
            "usage": usage
        })

        # Emit success response
        await context.emit({
            "topic": "chat.response",
            "data": {
                "response": content,
                "model": model,
                "usage": usage,
                "user_trace_id": user_trace_id,
                "status": "completed",
            }
        })

    except Exception as error:
        context.logger.error("OpenAI Chat Processor - Error", {
            "trace_id": context.trace_id,
            "error": str(error),
            "model": model
        })

        # Emit error response
        await context.emit({
            "topic": "chat.response",
            "data": {
                "error": str(error),
                "user_trace_id": user_trace_id,
                "status": "error",
            }
        })
