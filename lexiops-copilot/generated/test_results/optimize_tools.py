#!/usr/bin/env python3
"""
Create optimized tools prompt with only essential tools
"""
import json
import os

def create_optimized_tools():
    """Create optimized prompt with essential tools only"""
    
    # Load full tools
    with open("mcp_tools_extracted.json", "r", encoding="utf-8") as f:
        all_tools = json.load(f)
    
    # Essential tools for most Kubernetes operations
    essential_tools = [
        "kubectl",          # Most flexible and reliable
        "k8s_get",         # Get resources
        "k8s_logs",        # View logs
        "k8s_describe",    # Describe resources
        "k8s_create",      # Create resources
        "k8s_delete",      # Delete resources
        "k8s_scale",       # Scale resources
        "k8s_apply",       # Apply YAML
        "k8s_rollout_status", # Check deployments
        "k8s_events",      # View events
        "k8s_top_pods",    # Resource usage
        "helm"             # Helm operations
    ]
    
    # Filter tools
    optimized_tools = []
    for tool in all_tools:
        if tool["name"] in essential_tools:
            optimized_tools.append(tool)
    
    # Generate optimized prompt
    prompt_parts = [
        "ESSENTIAL KUBERNETES TOOLS:",
        ""
    ]
    
    for tool in optimized_tools:
        prompt_parts.append(f"**{tool['name']}**:")
        prompt_parts.append(f"  Description: {tool['description']}")
        
        if tool['input_schema']['properties']:
            prompt_parts.append("  Parameters:")
            for prop_name, prop_info in tool['input_schema']['properties'].items():
                required = prop_name in tool['input_schema']['required']
                req_text = " (required)" if required else " (optional)"
                description = prop_info.get('description', '').split('\n')[0]  # First line only
                prompt_parts.append(f"    - {prop_name}{req_text}: {description}")
        
        prompt_parts.append("")
    
    optimized_prompt = "\n".join(prompt_parts)
    
    # Save optimized files
    with open("mcp_tools_optimized.json", "w", encoding="utf-8") as f:
        json.dump(optimized_tools, f, indent=2, ensure_ascii=False)
    
    with open("mcp_tools_optimized_prompt.txt", "w", encoding="utf-8") as f:
        f.write(optimized_prompt)
    
    print(f"✅ Created optimized tools:")
    print(f"  - Original tools: {len(all_tools)}")
    print(f"  - Optimized tools: {len(optimized_tools)}")
    print(f"  - Original prompt: {len(open('mcp_tools_prompt.txt').read())} chars")
    print(f"  - Optimized prompt: {len(optimized_prompt)} chars")
    print(f"  - Reduction: {((len(open('mcp_tools_prompt.txt').read()) - len(optimized_prompt)) / len(open('mcp_tools_prompt.txt').read()) * 100):.1f}%")
    
    print(f"\n🔧 Optimized tools:")
    for tool in optimized_tools:
        print(f"  - {tool['name']}")

if __name__ == "__main__":
    create_optimized_tools()
