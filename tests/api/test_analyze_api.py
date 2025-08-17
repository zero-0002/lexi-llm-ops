#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test analyze legal query API endpoint
"""
import requests
import json

def test_analyze_endpoint():
    """Test analyze endpoint with realistic legal query"""
    url = 'http://localhost:8000/api/legal-chat/analyze-legal-query'
    
    payload = {
        'conversation_id': 'test_conv_real',
        'user_id': 'test_user_real', 
        'query': 'Tôi muốn hỏi về quyền lợi của người lao động khi bị sa thải không có lý do chính đáng. Công ty có thể sa thải tôi bất cứ lúc nào không?'
    }

    print('🚀 Sending request to analyze endpoint...')
    print(f'📤 Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}')
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f'📊 Status: {response.status_code}')
        print(f'📝 Response: {response.text}')
        
        if response.status_code == 200:
            print('✅ SUCCESS: Query analyzed successfully!')
        else:
            print(f'❌ ERROR: Status {response.status_code}')
            
    except requests.exceptions.Timeout:
        print('⏱️ TIMEOUT: Request took longer than 60s (likely processing)')
    except Exception as e:
        print(f'💥 EXCEPTION: {str(e)}')

if __name__ == '__main__':
    test_analyze_endpoint()
