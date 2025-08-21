#!/usr/bin/env python3
"""
Test dynamic tools loading
"""
import sys
import os
sys.path.append('.')

from agent.nodes.planner_node import load_tools_prompt

def test_dynamic_tools():
    print("🔍 Testing dynamic tools loading...")
    
    # Test load_tools_prompt function
    tools_prompt = load_tools_prompt()
    
    print(f"📏 Tools prompt length: {len(tools_prompt)} characters")
    print(f"📄 First 500 characters:")
    print("-" * 50)
    print(tools_prompt[:500])
    print("-" * 50)
    
    # Count tools
    tool_count = tools_prompt.count("**") // 2  # Each tool has **toolname**
    print(f"🔧 Found {tool_count} tools in prompt")
    
    # Check for key tools
    key_tools = ["kubectl", "k8s_get", "k8s_logs", "k8s_create"]
    for tool in key_tools:
        if f"**{tool}**" in tools_prompt:
            print(f"✅ {tool} found in prompt")
        else:
            print(f"❌ {tool} NOT found in prompt")

if __name__ == "__main__":
    test_dynamic_tools()
