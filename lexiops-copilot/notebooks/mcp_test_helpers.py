#!/usr/bin/env python3
"""
MCP Test Helper Functions
Helper functions for testing MCP Kubernetes server in Jupyter notebooks
"""

import json
import aiohttp
import requests
import subprocess
import time

# Configuration
FASTAPI_URL = "http://localhost:8001"
MCP_DIRECT_URL = "http://localhost:8002"
MCP_URL = "http://localhost:8002/mcp/"

class MCPTester:
    """MCP testing helper class"""
    
    def __init__(self, mcp_url=MCP_URL):
        self.mcp_url = mcp_url
        
    async def initialize_session(self, client_name="mcp-test"):
        """Initialize MCP session and return session ID"""
        init_payload = {
            "jsonrpc": "2.0",
            "id": f"init-{client_name}",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": client_name,
                    "version": "1.0.0"
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream, application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.mcp_url, json=init_payload, headers=headers, timeout=10) as response:
                if response.status == 200:
                    session_id = response.headers.get('mcp-session-id')
                    if session_id:
                        headers["mcp-session-id"] = session_id
                        
                        # Send initialized notification
                        init_notification = {
                            "jsonrpc": "2.0",
                            "method": "notifications/initialized"
                        }
                        
                        async with session.post(self.mcp_url, json=init_notification, headers=headers, timeout=5):
                            pass
                        
                        return session_id, headers
                        
                raise Exception(f"Session initialization failed: {response.status}")
    
    async def list_tools(self):
        """List all available MCP tools"""
        try:
            session_id, headers = await self.initialize_session("tools-lister")
            
            tools_payload = {
                "jsonrpc": "2.0",
                "id": "tools-list",
                "method": "tools/list",
                "params": {}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.mcp_url, json=tools_payload, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        if "data:" in content:
                            for line in content.split('\n'):
                                if line.startswith('data:'):
                                    data = json.loads(line[5:].strip())
                                    if 'result' in data and 'tools' in data['result']:
                                        return data['result']['tools']
                                    elif 'error' in data:
                                        raise Exception(f"MCP Error: {data['error']}")
                        
            raise Exception("No tools data found")
            
        except Exception as e:
            print(f"❌ Failed to list tools: {e}")
            return []
    
    async def call_tool(self, tool_name, tool_params):
        """Call a specific MCP tool with parameters"""
        try:
            session_id, headers = await self.initialize_session("tool-caller")
            
            tool_payload = {
                "jsonrpc": "2.0",
                "id": f"call-{tool_name}",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": tool_params
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.mcp_url, json=tool_payload, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        if "data:" in content:
                            for line in content.split('\n'):
                                if line.startswith('data:'):
                                    data = json.loads(line[5:].strip())
                                    if 'result' in data:
                                        return {
                                            'success': True,
                                            'result': data['result']
                                        }
                                    elif 'error' in data:
                                        return {
                                            'success': False,
                                            'error': data['error']
                                        }
                        
            return {
                'success': False,
                'error': f"HTTP {response.status}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def kubectl(self, command):
        """Execute kubectl command through MCP"""
        result = await self.call_tool("kubectl", {"command": command})
        
        if result['success'] and 'content' in result['result']:
            content_data = result['result']['content']
            if isinstance(content_data, list) and content_data:
                return content_data[0].get('text', '')
            else:
                return str(content_data)
        else:
            return f"Error: {result.get('error', 'Unknown error')}"


# Utility functions
def test_fastapi_health(url=FASTAPI_URL):
    """Test FastAPI main server health"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return {
            'healthy': response.status_code == 200,
            'status': response.status_code,
            'message': 'FastAPI server is healthy' if response.status_code == 200 else f'Health check failed: {response.status_code}'
        }
    except Exception as e:
        return {
            'healthy': False,
            'status': None,
            'message': f'Connection failed: {e}'
        }

def test_fastapi_chat(message, url=FASTAPI_URL):
    """Test FastAPI chat endpoint"""
    try:
        payload = {"message": message}
        response = requests.post(f"{url}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'response': result.get('response', ''),
                'tool_results': result.get('tool_results', []),
                'tools_used': len(result.get('tool_results', []))
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def check_kubernetes_mcp():
    """Check if MCP server is running in Kubernetes"""
    try:
        result = subprocess.run([
            'kubectl', 'get', 'pods', '-n', 'lexiops-copilot', 
            '-l', 'app=mcp-k8s-server'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return {
                'accessible': True,
                'pods_output': result.stdout,
                'running': "Running" in result.stdout,
                'message': 'Kubernetes cluster accessible'
            }
        else:
            return {
                'accessible': False,
                'pods_output': '',
                'running': False,
                'message': f'kubectl error: {result.stderr}'
            }
    except subprocess.TimeoutExpired:
        return {
            'accessible': False,
            'pods_output': '',
            'running': False,
            'message': 'kubectl command timed out'
        }
    except Exception as e:
        return {
            'accessible': False,
            'pods_output': '',
            'running': False,
            'message': f'Error: {e}'
        }

# Test scenarios
async def run_basic_mcp_test():
    """Run basic MCP connectivity and tools list test"""
    print("🧪 Basic MCP Test")
    print("="*50)
    
    tester = MCPTester()
    
    try:
        tools = await tester.list_tools()
        tools_count = len(tools)
        
        print(f"✅ Found {tools_count} MCP tools!")
        
        if tools_count > 0:
            print("🔧 Sample tools:")
            for i, tool in enumerate(tools[:5], 1):
                description = tool.get('description', 'No description')[:60]
                print(f"  {i}. {tool['name']} - {description}...")
            
            return {
                'success': True,
                'tools_count': tools_count,
                'tools': tools
            }
        else:
            return {
                'success': False,
                'tools_count': 0,
                'tools': []
            }
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return {
            'success': False,
            'tools_count': 0,
            'error': str(e)
        }

async def run_kubectl_test():
    """Run kubectl commands through MCP"""
    print("🛠️ Kubectl Test via MCP")
    print("="*50)
    
    tester = MCPTester()
    
    test_commands = [
        "get pods -n lexiops-copilot",
        "get svc -n lexiops-copilot",
        "get deployment -n lexiops-copilot"
    ]
    
    results = []
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n🔧 Test {i}: kubectl {cmd}")
        
        try:
            output = await tester.kubectl(cmd)
            print(f"✅ Success! Result: {output[:100]}...")
            results.append({
                'command': cmd,
                'success': True,
                'output': output
            })
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append({
                'command': cmd,
                'success': False,
                'error': str(e)
            })
    
    successful = [r for r in results if r.get('success', False)]
    print(f"\n📊 Summary: {len(successful)}/{len(test_commands)} tests passed")
    
    return results

async def run_mock_llm_test():
    """Mock LLM using MCP tools"""
    print("🤖 Mock LLM Test")
    print("="*50)
    
    tester = MCPTester()
    
    # Simulate LLM decision making
    llm_tasks = [
        {
            'task': 'Get pods in lexiops-copilot namespace',
            'tool': 'kubectl',
            'params': {'command': 'get pods -n lexiops-copilot'}
        },
        {
            'task': 'Check deployment status',
            'tool': 'kubectl', 
            'params': {'command': 'get deployment -n lexiops-copilot -o wide'}
        }
    ]
    
    results = []
    
    for i, task in enumerate(llm_tasks, 1):
        print(f"\n🧠 LLM Task {i}: {task['task']}")
        print(f"🔧 Using tool: {task['tool']} with params: {task['params']}")
        
        result = await tester.call_tool(task['tool'], task['params'])
        
        if result['success']:
            content = result['result'].get('content', [])
            if content and isinstance(content, list):
                output = content[0].get('text', '')[:150]
                print(f"✅ Success! Output: {output}...")
                results.append({
                    'task': task['task'],
                    'success': True,
                    'output': output
                })
            else:
                print(f"✅ Success! Raw result: {str(result['result'])[:100]}...")
                results.append({
                    'task': task['task'],
                    'success': True,
                    'output': str(result['result'])
                })
        else:
            print(f"❌ Failed: {result['error']}")
            results.append({
                'task': task['task'],
                'success': False,
                'error': result['error']
            })
    
    successful = [r for r in results if r.get('success', False)]
    print(f"\n🎯 LLM Tasks: {len(successful)}/{len(llm_tasks)} completed successfully")
    
    return results

# Quick test function
async def quick_test():
    """Run all tests quickly"""
    print("🚀 Quick MCP Test Suite")
    print("="*60)
    
    # Test 1: Basic MCP
    basic_result = await run_basic_mcp_test()
    
    print("\n")
    
    # Test 2: Kubectl 
    kubectl_results = await run_kubectl_test()
    
    print("\n")
    
    # Test 3: Mock LLM
    llm_results = await run_mock_llm_test()
    
    print("\n" + "="*60)
    print("🎉 Test Suite Summary:")
    print(f"✅ MCP Tools Available: {basic_result.get('tools_count', 0)}")
    print(f"✅ Kubectl Commands: {len([r for r in kubectl_results if r.get('success')])}/{len(kubectl_results)}")
    print(f"✅ LLM Tasks: {len([r for r in llm_results if r.get('success')])}/{len(llm_results)}")
    
    return {
        'basic': basic_result,
        'kubectl': kubectl_results,
        'llm': llm_results
    }
