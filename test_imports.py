#!/usr/bin/env python3
"""
Test script to diagnose import issues
Run this to see what's causing the main app to fail
"""

def test_imports():
    """Test all imports step by step"""
    print("🧪 Testing imports step by step...")
    
    # Test basic Python imports
    try:
        import os
        import sys
        print("✅ Basic Python imports: OK")
    except Exception as e:
        print(f"❌ Basic Python imports failed: {e}")
        return False
    
    # Test Flask imports
    try:
        from flask import Flask
        print("✅ Flask import: OK")
    except Exception as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    # Test Flask extensions
    try:
        from flask_sqlalchemy import SQLAlchemy
        from flask_login import LoginManager
        print("✅ Flask extensions: OK")
    except Exception as e:
        print(f"❌ Flask extensions failed: {e}")
        return False
    
    # Test AI/ML imports
    try:
        import numpy as np
        print("✅ NumPy: OK")
    except Exception as e:
        print(f"❌ NumPy failed: {e}")
    
    try:
        import cv2
        print("✅ OpenCV: OK")
    except Exception as e:
        print(f"❌ OpenCV failed: {e}")
    
    try:
        import torch
        print("✅ PyTorch: OK")
    except Exception as e:
        print(f"❌ PyTorch failed: {e}")
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe: OK")
    except Exception as e:
        print(f"❌ MediaPipe failed: {e}")
    
    # Test app imports
    try:
        from models import db, User
        print("✅ Models import: OK")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        from forms import LoginForm
        print("✅ Forms import: OK")
    except Exception as e:
        print(f"❌ Forms import failed: {e}")
        return False
    
    try:
        from auth_utils import AuthManager
        print("✅ Auth utils import: OK")
    except Exception as e:
        print(f"❌ Auth utils import failed: {e}")
        return False
    
    # Test main app import
    try:
        import app
        print("✅ Main app import: OK")
        return True
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Exercise Analyzer Import Test")
    print("=" * 40)
    success = test_imports()
    if success:
        print("\n🎉 All imports successful!")
    else:
        print("\n💥 Some imports failed - check the errors above")
