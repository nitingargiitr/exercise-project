#!/usr/bin/env python3
"""
Test script to identify which import is causing the Gunicorn error
"""
import sys
import traceback

def test_imports():
    """Test each import step by step"""
    print("🧪 Testing imports step by step...")
    
    # Test basic imports
    try:
        import os
        import sys
        import time
        from datetime import datetime, timedelta, date
        from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, flash, current_app
        from flask_login import LoginManager, login_user, logout_user, login_required, current_user
        from werkzeug.utils import secure_filename
        import tempfile
        import shutil
        print("✅ Basic imports: OK")
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        traceback.print_exc()
        return False
    
    # Test AI/ML imports
    try:
        import cv2
        import torch
        import numpy as np
        import mediapipe as mp
        from pushup_lstm import PushupLSTM
        from dataset_angles import calculate_angle
        print("✅ AI/ML imports: OK")
    except Exception as e:
        print(f"❌ AI/ML imports failed: {e}")
        traceback.print_exc()
    
    # Test models import
    try:
        from models import db, User, UserSession, ExerciseHistory, UserLevel, Achievement, UserAchievement, Card, UserCard, DailyChallenge, UserDailyChallenge
        print("✅ Models import: OK")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test forms import
    try:
        from forms import LoginForm, SignupForm, ForgotPasswordForm
        print("✅ Forms import: OK")
    except Exception as e:
        print(f"❌ Forms import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test auth utils import
    try:
        from auth_utils import AuthManager, GoogleOAuth
        print("✅ Auth utils import: OK")
    except Exception as e:
        print(f"❌ Auth utils import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test gamification import
    try:
        from gamification import GamificationManager, initialize_gamification_data
        print("✅ Gamification import: OK")
    except Exception as e:
        print(f"❌ Gamification import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test full app import
    try:
        import app
        print("✅ Full app import: OK")
        return True
    except Exception as e:
        print(f"❌ Full app import failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Exercise Analyzer Import Test")
    print("=" * 50)
    success = test_imports()
    if success:
        print("\n🎉 All imports successful!")
        sys.exit(0)
    else:
        print("\n💥 Import test failed!")
        sys.exit(1)
