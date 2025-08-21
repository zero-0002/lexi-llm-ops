"""
Test script cho OpenAI-powered Agent workflow
"""
import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_ai_agent():
    """Test the AI-powered agent with various inputs"""
    
    base_url = "http://localhost:8000"
    
    # Kiểm tra API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not found in environment variables.")
        print("📝 Please create .env file with your OpenAI API key:")
        print("   OPENAI_API_KEY=your_actual_api_key_here")
        return
    
    test_cases = [
        {
            "input": "What's the current time and system info?",
            "description": "Multi-tool request - should intelligently plan"
        },
        {
            "input": "I need to analyze some data, can you help?", 
            "description": "Ambiguous request - should ask for clarification or provide options"
        },
        {
            "input": "Show me the current time",
            "description": "Simple time request"
        },
        {
            "input": "Can you read the README file for me?",
            "description": "File reading request"
        },
        {
            "input": "What can you do? What tools do you have?",
            "description": "Capability inquiry"
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Health check first
        try:
            print("🔍 Checking agent health...")
            response = await client.get(f"{base_url}/health")
            health = response.json()
            print(f"Health status: {health}")
            print()
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return
        
        # Test each case
        for i, test_case in enumerate(test_cases, 1):
            print(f"🧪 Test {i}: {test_case['description']}")
            print(f"💬 Input: {test_case['input']}")
            
            try:
                response = await client.post(
                    f"{base_url}/chat",
                    json={"message": test_case['input']}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Status: {result['status']}")
                    print(f"🤖 AI Response: {result['response'][:200]}...")
                    if len(result['response']) > 200:
                        print(f"    [...{len(result['response'])-200} more chars]")
                    print(f"🔧 Tools used: {len(result.get('tool_results', []))}")
                    
                    if result.get('tool_results'):
                        for j, tool_result in enumerate(result['tool_results'], 1):
                            tool_name = tool_result.get('name', 'unknown')
                            print(f"   {j}. Tool: {tool_name}")
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Test failed: {e}")
            
            print("-" * 70)
            print()

async def test_single_query(query: str):
    """Test a single query"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"🧪 Testing: {query}")
            response = await client.post(
                f"{base_url}/chat",
                json={"message": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {result['response']}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test single query from command line
        query = " ".join(sys.argv[1:])
        asyncio.run(test_single_query(query))
    else:
        # Run full test suite
        asyncio.run(test_ai_agent())
