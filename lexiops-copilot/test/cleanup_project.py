#!/usr/bin/env python3
"""
Project cleanup script - organize and clean up generated files
"""
import os
import shutil
import json
from datetime import datetime

def cleanup_project():
    """Clean up and organize project files"""
    print("🧹 PROJECT CLEANUP")
    print("=" * 50)
    
    # Create organized directories
    dirs_to_create = [
        "generated",
        "generated/mcp_tools",
        "generated/test_results", 
        "backup/original_files",
        "docs/mcp_integration"
    ]
    
    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")
    
    # Files to move to generated/mcp_tools/
    mcp_files = [
        "mcp_tools_full.json",
        "mcp_tools_extracted.json", 
        "mcp_tools_optimized.json",
        "mcp_tools_prompt.txt",
        "mcp_tools_optimized_prompt.txt"
    ]
    
    print(f"\n📦 Moving MCP tools files...")
    for file in mcp_files:
        if os.path.exists(file):
            shutil.move(file, f"generated/mcp_tools/{file}")
            print(f"  ✅ Moved {file} → generated/mcp_tools/")
        else:
            print(f"  ⚠️  {file} not found")
    
    # Test files to move to generated/test_results/
    test_files = [
        "get_mcp_tools.py",
        "optimize_tools.py", 
        "test_dynamic_tools.py",
        "demo_mcp_optimization.py"
    ]
    
    print(f"\n🧪 Moving test/utility files...")
    for file in test_files:
        if os.path.exists(file):
            shutil.move(file, f"generated/test_results/{file}")
            print(f"  ✅ Moved {file} → generated/test_results/")
        else:
            print(f"  ⚠️  {file} not found")
    
    # Files to keep in root (core functionality)
    core_files = [
        "quick_test.py",
        "test_fastapi_mcp.py",
        "test_mcp.py",
        "requirements.txt"
    ]
    
    print(f"\n📋 Core files remaining in root:")
    for file in core_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} missing")
    
    # Update planner_node.py to use new paths
    print(f"\n🔧 Updating file paths in planner_node.py...")
    update_planner_paths()
    
    # Create summary file
    create_cleanup_summary()
    
    print(f"\n✨ CLEANUP COMPLETED!")
    print(f"📁 Project structure organized")
    print(f"🔧 File paths updated") 
    print(f"📄 Summary created in generated/cleanup_summary.json")

def update_planner_paths():
    """Update paths in planner_node.py to point to new locations"""
    planner_file = "agent/nodes/planner_node.py"
    
    if not os.path.exists(planner_file):
        print(f"  ❌ {planner_file} not found")
        return
    
    with open(planner_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update paths to point to generated/mcp_tools/
    old_patterns = [
        "'mcp_tools_optimized_prompt.txt'",
        "'mcp_tools_prompt.txt'", 
        "'mcp_tools_extracted.json'"
    ]
    
    new_patterns = [
        "'generated', 'mcp_tools', 'mcp_tools_optimized_prompt.txt'",
        "'generated', 'mcp_tools', 'mcp_tools_prompt.txt'",
        "'generated', 'mcp_tools', 'mcp_tools_extracted.json'"
    ]
    
    for old, new in zip(old_patterns, new_patterns):
        if old in content:
            content = content.replace(
                f"'..', '..', {old}",
                f"'..', '..', {new}"
            )
    
    with open(planner_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Updated paths in {planner_file}")

def create_cleanup_summary():
    """Create summary of cleanup operations"""
    summary = {
        "cleanup_date": datetime.now().isoformat(),
        "directories_created": [
            "generated/",
            "generated/mcp_tools/", 
            "generated/test_results/",
            "backup/original_files/",
            "docs/mcp_integration/"
        ],
        "files_moved": {
            "mcp_tools": [
                "mcp_tools_full.json",
                "mcp_tools_extracted.json", 
                "mcp_tools_optimized.json",
                "mcp_tools_prompt.txt",
                "mcp_tools_optimized_prompt.txt"
            ],
            "test_results": [
                "get_mcp_tools.py",
                "optimize_tools.py",
                "test_dynamic_tools.py", 
                "demo_mcp_optimization.py"
            ]
        },
        "core_files_root": [
            "quick_test.py",
            "test_fastapi_mcp.py", 
            "test_mcp.py",
            "requirements.txt"
        ],
        "updated_files": [
            "agent/nodes/planner_node.py"
        ],
        "description": "Organized project structure for better maintainability"
    }
    
    with open("generated/cleanup_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    cleanup_project()
