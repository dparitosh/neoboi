#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from backend.main import app
    print("App imported successfully")

    # Test cache service
    from backend.cache_service import get_cache_service
    cache = get_cache_service()
    print("Cache service initialized")

    # Test routes
    from backend.routes.routes import router
    print("Routes imported successfully")

    print("All imports successful")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()