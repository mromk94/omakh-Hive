#!/usr/bin/env python3
"""Test if main.py imports correctly"""

try:
    print("Testing imports...")
    import main
    print("✅ main.py imports successfully")
    
    app = main.create_app()
    print(f"✅ FastAPI app created: {app}")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
