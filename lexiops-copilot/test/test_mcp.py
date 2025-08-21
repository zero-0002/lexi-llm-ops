#!/usr/bin/env python3
"""
Test script for MCP Kubernetes server
"""
import asyncio
import aiohttp
import json

async def test_mcp_server():
    """Test MCP server with proper headers and protocol"""
    
    url = "http://localhost:8002/mcp/"
    
    # First, try to initialize a session
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
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    print(f"🔍 Testing MCP server at {url}")
    print(f"� Step 1: Initializing session")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Initialize session
            async with session.post(url, json=init_payload, headers=init_headers, timeout=10) as response:
                print(f"📊 Init Status: {response.status}")
                
                if response.status != 200:
                    content = await response.text()
                    print(f"❌ Init failed: {content}")
                    return
                
                # Get session ID from response headers
                session_id = response.headers.get('mcp-session-id')
                print(f"🔑 Session ID: {session_id}")
                
                if not session_id:
                    print("❌ No session ID received")
                    return
                
                # Send initialized notification
                print(f"🚀 Step 2: Sending initialized notification")
                
                initialized_headers = {
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream, application/json",
                    "mcp-session-id": session_id
                }
                
                initialized_payload = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                
                async with session.post(url, json=initialized_payload, headers=initialized_headers, timeout=5) as init_response:
                    print(f"📊 Initialized Status: {init_response.status}")
                    if init_response.status != 200:
                        content = await init_response.text()
                        print(f"⚠️  Init notification response: {content}")
                
                # Now test tools/list with session ID
                print(f"🚀 Step 3: Listing tools")
                
                tools_headers = {
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream, application/json",
                    "mcp-session-id": session_id
                }
                
                tools_payload = {
                    "jsonrpc": "2.0",
                    "id": "tools-1",
                    "method": "tools/list",
                    "params": {}
                }
                
                async with session.post(url, json=tools_payload, headers=tools_headers, timeout=10) as tools_response:
                    print(f"📊 Tools Status: {tools_response.status}")
                    
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
                                        if 'error' in parsed:
                                            print(f"❌ Tools Error: {parsed['error']}")
                                        else:
                                            print(f"✅ Tools Response: {json.dumps(parsed, indent=2)}")
                                    except json.JSONDecodeError:
                                        print(f"📄 Raw data: {data}")
                        else:
                            print(f"📄 Raw Response: {content}")
                    else:
                        content = await tools_response.text()
                        print(f"❌ Tools HTTP Error: {content}")
                    
    except asyncio.TimeoutError:
        print("⏱️  Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
