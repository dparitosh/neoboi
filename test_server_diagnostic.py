#!/usr/bin/env python3
"""
Minimal server test to isolate the startup issue
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test basic imports"""
    print("Testing basic imports...")
    try:
        import fastapi
        print("✓ FastAPI imported")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False

    try:
        import uvicorn
        print("✓ Uvicorn imported")
    except ImportError as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False

    return True

def test_minimal_app():
    """Test creating a minimal FastAPI app"""
    print("\nTesting minimal FastAPI app...")
    try:
        from fastapi import FastAPI

        app = FastAPI(title="Test App", description="Minimal test app", version="1.0.0")
        print("✓ Minimal FastAPI app created")

        @app.get("/")
        async def root():
            return {"message": "Test app running"}

        print("✓ Root endpoint added")
        return app
    except Exception as e:
        print(f"✗ Minimal app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_main_app():
    """Test importing the main app"""
    print("\nTesting main app import...")
    try:
        from backend.main import app
        print("✓ Main app imported successfully")
        return app
    except Exception as e:
        print(f"✗ Main app import failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_server_start(app, port=3002):
    """Test starting the server"""
    print(f"\nTesting server start with {type(app).__name__} on port {port}...")
    try:
        import uvicorn
        import threading
        import time

        # Start server in background thread
        def run_server():
            try:
                uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
            except Exception as e:
                print(f"Server thread exception: {e}")

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Wait a bit and check if server is still running
        time.sleep(3)

        if server_thread.is_alive():
            print("✓ Server appears to be running")
            # Try to make a request to verify it's actually responding
            try:
                import requests
                response = requests.get(f"http://127.0.0.1:{port}/", timeout=1)
                if response.status_code == 200:
                    print("✓ Server is responding to requests")
                else:
                    print(f"✗ Server responded with status {response.status_code}")
            except Exception as e:
                print(f"✗ Server not responding to requests: {e}")
            return True
        else:
            print("✗ Server thread died")
            return False

    except Exception as e:
        print(f"✗ Server start test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== NeoBoi Server Diagnostic Test ===\n")

    # Test 1: Basic imports
    if not test_imports():
        sys.exit(1)

    # Test 2: Minimal app
    minimal_app = test_minimal_app()
    if minimal_app is None:
        sys.exit(1)

    # Test 3: Test server with minimal app
    if not test_server_start(minimal_app, port=3002):
        print("Even minimal app won't start - this suggests a deeper issue")
        sys.exit(1)

    # Test 4: Main app import
    main_app = test_main_app()
    if main_app is None:
        print("Main app import failed - check the main.py file")
        sys.exit(1)

    # Test 5: Test server with main app
    if not test_server_start(main_app, port=3003):
        print("Main app imports but won't start - check for runtime issues")
        sys.exit(1)

    print("\n✓ All tests passed!")