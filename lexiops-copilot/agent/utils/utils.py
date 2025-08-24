def parse_output_llm(message_raw: str,name: bool = False) -> dict:
    """
    Phân tích đầu ra từ LLM và trích xuất thông tin cần thiết.
    """
    tool_calls = message_raw.additional_kwargs.get("tool_calls", [])
    if len(tool_calls) > 0:
        arguments_str = tool_calls[0]["function"]["arguments"]
        if name:
            name = tool_calls[0]["function"]["name"]
            return arguments_str + ", " + name
    return arguments_str