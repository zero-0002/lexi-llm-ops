#!/usr/bin/env python3
"""
FastAPI MCP Integration Test Script
Tests CRUD operations with Kubernetes through MCP tools
"""

import requests
import json
import time

FASTAPI_URL = "http://localhost:8001"

def test_k8s_operation(message, description):
    """Test a Kubernetes operation through FastAPI + MCP"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Request: {message}")
    
    try:
        payload = {"message": message}
        response = requests.post(f"{FASTAPI_URL}/chat", json=payload, timeout=45)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: {result.get('response', '')[:200]}...")
            
            if result.get('tool_results'):
                print(f"Tools used: {len(result['tool_results'])}")
                for i, tool_result in enumerate(result['tool_results'][:3]):
                    print(f"   {i+1}. {tool_result.get('name', 'unknown')}: {str(tool_result.get('content', ''))[:100]}...")
                return True
            else:
                print("WARNING: No MCP tools were executed")
                return False
        else:
            print(f"ERROR: {response.text}")
            return False
            
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def main():
    """Main test suite"""
    print("FastAPI + MCP Kubernetes Integration Test")
    print("="*60)
    
    # Test 1: List pods (READ operation)
    success1 = test_k8s_operation(
        "List all pods in the lexiops-copilot namespace", 
        "Test 1: List Pods (READ)"
    )
    
    # Test 2: Get services (READ operation)
    success2 = test_k8s_operation(
        "Show me all services in lexiops-copilot namespace",
        "Test 2: List Services (READ)"
    )
    
    # Test 3: Get deployment info (READ operation)
    success3 = test_k8s_operation(
        "Get information about mcp-k8s-deployment in lexiops-copilot namespace",
        "Test 3: Get Deployment Info (READ)"
    )
    
    # Test 4: Create a simple pod (CREATE operation)
    success4 = test_k8s_operation(
        "Create a test pod named 'test-nginx' using nginx image in lexiops-copilot namespace",
        "Test 4: Create Pod (CREATE)"
    )
    
    # Wait a bit for pod to be created
    if success4:
        print("\nWaiting 5 seconds for pod creation...")
        time.sleep(5)
    
    # Test 5: List pods again to see new pod
    success5 = test_k8s_operation(
        "List all pods in lexiops-copilot namespace to see the new test-nginx pod",
        "Test 5: Verify Pod Creation (READ)"
    )
    
    # Test 6: Delete the test pod (DELETE operation)
    success6 = test_k8s_operation(
        "Delete the test-nginx pod from lexiops-copilot namespace",
        "Test 6: Delete Pod (DELETE)"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    tests = [
        ("List Pods", success1),
        ("List Services", success2), 
        ("Get Deployment", success3),
        ("Create Pod", success4),
        ("Verify Creation", success5),
        ("Delete Pod", success6)
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        print(f"  {'PASS' if success else 'FAIL'} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("ALL TESTS PASSED! FastAPI + MCP + Kubernetes integration is working!")
    elif passed > total // 2:
        print("PARTIAL SUCCESS! Most operations are working.")
    else:
        print("MAJOR ISSUES! Check FastAPI, MCP server, and Kubernetes connectivity.")

if __name__ == "__main__":
    main()
