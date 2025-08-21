#!/usr/bin/env python3
"""
Advanced JSON parsing utilities for LexiOps Copilot
"""
import json
import re
from typing import Dict, Any, List, Optional
import logging
from langchain_openai import ChatOpenAI
import os

logger = logging.getLogger(__name__)


def load_tools_prompt() -> str:
    """Load tools from JSON and generate prompt text"""
    try:
        json_file = "list_tools.json"
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                tools = json.load(f)
            json_string = json.dumps(tools, indent=2)
            return json_string
    except Exception as e:
        print(f"Warning: Could not load tools from JSON: {e}")
        logger.info(f"Could not load tools from JSON: {e}")
        return str(e)


class JSONParser:
    """Advanced JSON parser with multiple strategies"""
    
    # Template structure for validation
    EXPECTED_STRUCTURE = {
        "thought": "string",
        "tool_calls": [
            {
                "name": "string",
                "args": {
                    "resource_type": "string",
                    "name": "string", 
                    "namespace": "string"
                }
            }
        ]
    }
    
    # Key patterns to look for
    KEY_PATTERNS = [
        "thought",
        "tool_calls", 
        "name",
        "args",
        "resource_type",
        "namespace",
        "command",
        "reason"
    ]

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Step 1: Normalize text to lowercase and clean
        """
        # Convert to lowercase for pattern matching
        normalized = text.lower()
        
        # Remove common markdown artifacts
        normalized = re.sub(r'```json\s*', '', normalized)
        normalized = re.sub(r'```\s*', '', normalized)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Fix common JSON issues
        normalized = re.sub(r',\s*}', '}', normalized)  # Remove trailing commas
        normalized = re.sub(r',\s*]', ']', normalized)
        
        return normalized

    @staticmethod
    def extract_with_regex_strategies(text: str) -> Optional[Dict[str, Any]]:
        """
        Step 2: Multiple regex strategies for JSON extraction
        """
        strategies = [
            # Strategy 1: Balanced braces
            JSONParser._extract_balanced_braces,
            # Strategy 2: JSON-like pattern
            JSONParser._extract_json_pattern,

            JSONParser._repair_with_llm
        ]
        
        for strategy in strategies:
            try:
                result = strategy(text)
                if result and JSONParser._validate_basic_structure(result):
                    return result
            except Exception as e:
                print(f"Strategy {strategy.__name__} failed: {e}")
                continue
            logging.debug(f"Strategy {strategy.__name__} succeeded")
        return None

    @staticmethod
    def _extract_balanced_braces(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON using balanced brace counting"""
        brace_count = 0
        start_idx = -1
        
        for i, char in enumerate(text):
            if char == '{':
                if start_idx == -1:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    json_str = text[start_idx:i+1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        continue
        return None

    @staticmethod
    def _extract_json_pattern(text: str) -> Optional[Dict[str, Any]]:
        """Extract using comprehensive JSON regex pattern"""
        # More comprehensive pattern
        json_pattern = r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                clean_match = match.strip()
                # Fix common issues
                clean_match = re.sub(r',(\s*[}\]])', r'\1', clean_match)
                return json.loads(clean_match)
            except json.JSONDecodeError:
                continue
        return None

    @staticmethod
    def _repair_with_llm(broken_json_string: str) -> Optional[str]:
        """
        Sử dụng LLM để sửa các lỗi JSON phức tạp hơn.
        """
        print("--- [Editor] Sửa lỗi bằng LLM... ---")
        prompt = f"""
        You are an expert JSON repair bot. Your SOLE task is to fix a broken JSON string.
        The following string is almost valid JSON but has syntax errors.
        Return ONLY the corrected, valid JSON object. Do not add any explanation, comments, or surrounding text.

        Broken JSON:
        {broken_json_string}

        Corrected JSON:
        """
        try:
            repair_llm = ChatOpenAI(model="gpt-4.1-nano", openai_api_key=os.getenv("OPENAI_API_KEY"))
            response = repair_llm.invoke(prompt).content.strip().lower()
            try:
                response = JSONParser._extract_balanced_braces(response)
            except Exception as e:
                response = JSONParser._extract_json_pattern(response)
            return response
        except Exception as e:
            print(f"--- [Editor] Lỗi khi gọi LLM sửa lỗi: {e} ---")
            return None

    @staticmethod
    def _validate_basic_structure(data: Dict[str, Any]) -> bool:
        """Basic validation of extracted data"""
        if not isinstance(data, dict):
            return False
        
        # Check for required keys
        if "tool_calls" not in data:
            return False
        
        if not isinstance(data["tool_calls"], list):
            return False
        
        # Check tool calls structure
        for tool_call in data["tool_calls"]:
            if not isinstance(tool_call, dict):
                return False
            if "name" not in tool_call:
                return False
        
        return True

    @staticmethod
    def _validate_template_match(data: Dict[str, Any]) -> bool:
        """Validate against template structure"""
        if not JSONParser._validate_basic_structure(data):
            return False
        
        # Check if we have meaningful data
        if "thought" in data and data["thought"]:
            return True
        
        if data["tool_calls"]:
            tool_call = data["tool_calls"][0]
            if tool_call.get("name") and tool_call.get("args"):
                return True
        
        return False

    @classmethod
    def parse_json_response(cls, text: str) -> Dict[str, Any]:
        """
        Main parsing function with all strategies
        """
        print(f"🔍 Parsing JSON from text: {text[:100]}...")
        
        # Step 1: Normalize
        normalized = cls.normalize_text(text)
        print(f"📝 Normalized: {normalized[:100]}...")
        
        # Step 2: Try regex strategies
        result = cls.extract_with_regex_strategies(text)  # Use original text
        if result:
            print(f"✅ Regex extraction successful: {result}")
            return result
        
        # Step 3: Try template matching
        result = cls.extract_with_template_matching(text)
        if result:
            print(f"✅ Template extraction successful: {result}")
            return result
        
        # Step 4: Fallback
        print("⚠️ All parsing strategies failed, using fallback")
        return cls._create_fallback_response(text)

    @staticmethod
    def _create_fallback_response(text: str) -> Dict[str, Any]:
        """Create fallback response based on text analysis"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["list", "get", "show", "pods", "service", "deployment"]):
            return {
                "thought": "User wants to list or view Kubernetes resources",
                "tool_calls": [
                    {
                        "name": "kubectl",
                        "args": {"command": "get pods -n lexiops-copilot"}
                    }
                ]
            }
        elif "time" in text_lower:
            return {
                "thought": "User asked for current time",
                "tool_calls": [
                    {
                        "name": "get_current_time",
                        "args": {}
                    }
                ]
            }
        else:
            return {
                "thought": "Default cluster status check",
                "tool_calls": [
                    {
                        "name": "kubectl", 
                        "args": {"command": "get pods -n lexiops-copilot"}
                    }
                ]
            }

# Convenience function for backwards compatibility
def extract_json_with_regex(text: str) -> Dict[str, Any]:
    """
    Enhanced JSON extraction function
    """
    return JSONParser.parse_json_response(text)
