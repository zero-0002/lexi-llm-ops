import requests
import json

def quick_test():
    """Quick test of FastAPI + MCP integration"""
    print("Quick FastAPI + MCP Test")
    print("=" * 40)
    
    url = "http://localhost:8001/chat"
    
    # Test 1: List pods
    print("Test 1: List pods")
    try:
        response = requests.post(url, json={"message": "List pods"}, timeout=20)
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: {result['response'][:100]}...")
            print(f"Tools: {len(result.get('tool_results', []))}")
            
            # Show tool details
            for tool in result.get('tool_results', []):
                tool_name = tool.get('name', 'unknown')
                content = str(tool.get('content', ''))[:200]
                print(f"  - {tool_name}: {content}...")
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\nDone!")

if __name__ == "__main__":
    quick_test()
