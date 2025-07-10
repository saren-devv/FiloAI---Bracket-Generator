#!/usr/bin/env python3
"""
Test file to verify imports work correctly
"""

try:
    import flask
    print("✅ Flask imported successfully")
    print(f"   Version: {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")

try:
    import flask_cors
    print("✅ Flask-CORS imported successfully")
    print(f"   Version: {flask_cors.__version__}")
except ImportError as e:
    print(f"❌ Flask-CORS import failed: {e}")

try:
    import pandas
    print("✅ Pandas imported successfully")
except ImportError as e:
    print(f"❌ Pandas import failed: {e}")

try:
    import openpyxl
    print("✅ OpenPyXL imported successfully")
except ImportError as e:
    print(f"❌ OpenPyXL import failed: {e}")

print("\n🎯 All import tests completed!") 