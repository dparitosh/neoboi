#!/usr/bin/env python3
"""
Test script to start the server and test the chat endpoint
"""
import sys
import os
import time
import threading
import requests
from backend.main import app
import uvicorn

def test_chat_endpoint():
    """Test the chat endpoint"""
    print("Waiting for server to start...")
    time.sleep(8)  # Wait longer for server to start

    # First check health endpoint
    try:
        health_response = requests.get('http://localhost:3001/health', timeout=5)
        print(f'Health check - Status: {health_response.status_code}')
        if health_response.status_code == 200:
            print(f'Health response: {health_response.json()}')
        else:
            print(f'Health check failed: {health_response.text}')
            return
    except Exception as e:
        print(f'Health check error: {e}')
        return

    # Now test chat endpoint
    try:
        print("Testing chat endpoint...")
        response = requests.post(
            'http://localhost:3001/api/chat',
            json={'query': 'What is Neo4j?'},
            timeout=15
        )

        print(f'Chat Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Response keys: {list(data.keys())}')
            text_response = data.get('textResponse', 'No response')
            print(f'Text response: {text_response[:200]}...')
        else:
            print(f'Error response: {response.text[:200]}')

    except Exception as e:
        print(f'Error testing chat endpoint: {e}')

if __name__ == '__main__':
    # Set PYTHONPATH
    sys.path.insert(0, 'd:\\Software\\boiSoftware\\neoboi')
    sys.path.insert(0, 'd:\\Software\\boiSoftware\\neoboi\\backend')

    print("Starting server in main thread...")
    # Start server in main thread - this will block
    try:
        uvicorn.run(app, host='127.0.0.1', port=3001, log_level='info', access_log=False)
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()