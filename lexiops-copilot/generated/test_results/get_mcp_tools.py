#!/usr/bin/env python3
"""
Script to get all MCP tools and save to JSON for prompt optimization
"""
import json
import asyncio
import aiohttp
from typing import Dict, List, Any

async def get_mcp_tools():
    """Get all available tools from MCP server using proper MCP protocol"""
    
    url = "http://localhost:8002/mcp/"
    
    # Initialize headers
    init_headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream, application/json"
    }
    
    init_payload = {
        "jsonrpc": "2.0",
        "id": "init-1",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "tools-extractor",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Initialize session
            async with session.post(url, json=init_payload, headers=init_headers, timeout=10) as response:
                if response.status != 200:
                    print(f"❌ Init failed: {response.status}")
                    return []
                
                # Get session ID
                session_id = response.headers.get('mcp-session-id')
                if not session_id:
                    print("❌ No session ID received")
                    return []
                
                print(f"🔑 Session ID: {session_id}")
                
                # Send initialized notification
                initialized_headers = {
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream, application/json",
                    "mcp-session-id": session_id
                }
                
                initialized_payload = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                
                await session.post(url, json=initialized_payload, headers=initialized_headers, timeout=5)
                
                # Get tools list
                tools_payload = {
                    "jsonrpc": "2.0",
                    "id": "tools-1",
                    "method": "tools/list",
                    "params": {}
                }
                
                async with session.post(url, json=tools_payload, headers=initialized_headers, timeout=10) as tools_response:
                    if tools_response.status == 200:
                        content = await tools_response.text()
                        
                        # Parse event stream data
                        if "data:" in content:
                            lines = content.split('\n')
                            for line in lines:
                                if line.startswith('data:'):
                                    data = line[5:].strip()
                                    try:
                                        parsed = json.loads(data)
                                        if 'result' in parsed and 'tools' in parsed['result']:
                                            return parsed['result']['tools']
                                    except json.JSONDecodeError:
                                        continue
                        
                        # Try direct JSON parse
                        try:
                            parsed = json.loads(content)
                            if 'result' in parsed and 'tools' in parsed['result']:
                                return parsed['result']['tools']
                        except json.JSONDecodeError:
                            pass
                    
                    print(f"❌ Tools request failed: {tools_response.status}")
                    return []
                    
    except Exception as e:
        print(f"❌ Error getting MCP tools: {e}")
        return []

def extract_tool_info(tools: List[Dict]) -> List[Dict]:
    """Extract essential tool information for prompt"""
    extracted = []
    
    for tool in tools:
        # Extract only essential fields for prompt
        tool_info = {
            "name": tool.get("name", ""),
            "description": tool.get("description", ""),
            "input_schema": {
                "type": tool.get("inputSchema", {}).get("type", "object"),
                "properties": {},
                "required": tool.get("inputSchema", {}).get("required", [])
            }
        }
        
        # Extract property descriptions only (not full schema)
        properties = tool.get("inputSchema", {}).get("properties", {})
        for prop_name, prop_schema in properties.items():
            tool_info["input_schema"]["properties"][prop_name] = {
                "type": prop_schema.get("type", "string"),
                "description": prop_schema.get("description", "")
            }
        
        extracted.append(tool_info)
    
    return extracted

def generate_tools_prompt(tools: List[Dict]) -> str:
    """Generate prompt text from tools for LLM"""
    prompt_parts = [
        "Available Kubernetes Tools:",
        ""
    ]
    
    for tool in tools:
        prompt_parts.append(f"**{tool['name']}**:")
        prompt_parts.append(f"  Description: {tool['description']}")
        
        if tool['input_schema']['properties']:
            prompt_parts.append("  Parameters:")
            for prop_name, prop_info in tool['input_schema']['properties'].items():
                required = prop_name in tool['input_schema']['required']
                req_text = " (required)" if required else " (optional)"
                prompt_parts.append(f"    - {prop_name}{req_text}: {prop_info['description']}")
        
        prompt_parts.append("")
    
    return "\n".join(prompt_parts)

async def main():
    print("🔍 Getting MCP tools...")
    
    # Get tools from MCP server
    tools = await get_mcp_tools()
    
    if not tools:
        print("❌ No tools found or error occurred")
        return
    
    print(f"✅ Found {len(tools)} tools")
    
    # Save full tools to JSON
    with open("mcp_tools_full.json", "w", encoding="utf-8") as f:
        json.dump(tools, f, indent=2, ensure_ascii=False)
    print("💾 Saved full tools to mcp_tools_full.json")
    
    # Extract essential info
    extracted_tools = extract_tool_info(tools)
    
    # Save extracted tools to JSON
    with open("mcp_tools_extracted.json", "w", encoding="utf-8") as f:
        json.dump(extracted_tools, f, indent=2, ensure_ascii=False)
    print("💾 Saved extracted tools to mcp_tools_extracted.json")
    
    # Generate prompt text
    prompt_text = generate_tools_prompt(extracted_tools)
    
    # Save prompt to text file
    with open("mcp_tools_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt_text)
    print("💾 Saved tools prompt to mcp_tools_prompt.txt")
    
    # Print summary
    print("\n📊 Tool Summary:")
    for tool in extracted_tools:
        print(f"  - {tool['name']}: {len(tool['input_schema']['properties'])} parameters")
    
    print(f"\n🎯 Prompt length: {len(prompt_text)} characters")
    print("\n🔧 Generated files:")
    print("  - mcp_tools_full.json (complete tool schemas)")
    print("  - mcp_tools_extracted.json (essential fields only)")
    print("  - mcp_tools_prompt.txt (formatted prompt text)")

if __name__ == "__main__":
    asyncio.run(main())
