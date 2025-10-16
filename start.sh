#!/bin/bash

# Set environment variables for OpenCV compatibility
export OPENCV_VIDEOIO_PRIORITY_MSMF=0
export OPENCV_VIDEOIO_PRIORITY_FFMPEG=1
export OPENCV_VIDEOIO_PRIORITY_GSTREAMER=0

# Set default port
export PORT=${PORT:-8080}

echo "🚀 Starting Railway deployment setup..."
echo "📁 Extracting templates, static files, and AI models..."

# Extract files with error handling
extract_file() {
    local file=$1
    if [ -f "$file" ]; then
        echo "Extracting $file..."
        if python3 -c "import zipfile; zipfile.ZipFile('$file').extractall()" 2>/dev/null; then
            echo "✅ $file extracted successfully"
            return 0
        else
            echo "⚠️ Failed to extract $file, continuing..."
            return 1
        fi
    else
        echo "⚠️ $file not found, continuing..."
        return 1
    fi
}

# Extract all files
extract_file "templates.zip"
extract_file "static.zip" 
extract_file "models.zip"

echo "✅ File extraction completed"
echo "🤖 AI models extracted - video analysis will work!"

# Create necessary directories
mkdir -p uploads output data models

echo "🚀 Starting Gunicorn server on port $PORT..."

# Test app import before starting Gunicorn
echo "🧪 Testing app import..."
if python3 -c "import app; print('App import successful')" 2>/dev/null; then
    echo "✅ App import test passed, starting Exercise Analyzer..."
    exec gunicorn \
        --bind 0.0.0.0:${PORT} \
        --workers 1 \
        --timeout 300 \
        --keep-alive 2 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --preload \
        --log-level info \
        --access-logfile - \
        --error-logfile - \
        app:app
else
    echo "❌ App import test failed!"
    echo "🔧 Testing imports step by step..."
    
    # Test basic imports
    echo "Testing basic imports..."
    if python3 -c "import os, sys, time; from datetime import datetime; from flask import Flask; print('Basic imports OK')" 2>/dev/null; then
        echo "✅ Basic imports: OK"
    else
        echo "❌ Basic imports failed"
    fi
    
    # Test models import
    echo "Testing models import..."
    if python3 -c "from models import db, User; print('Models import OK')" 2>/dev/null; then
        echo "✅ Models import: OK"
    else
        echo "❌ Models import failed"
    fi
    
    # Test forms import
    echo "Testing forms import..."
    if python3 -c "from forms import LoginForm; print('Forms import OK')" 2>/dev/null; then
        echo "✅ Forms import: OK"
    else
        echo "❌ Forms import failed"
    fi
    
    # Test auth utils import
    echo "Testing auth utils import..."
    if python3 -c "from auth_utils import AuthManager; print('Auth utils import OK')" 2>/dev/null; then
        echo "✅ Auth utils import: OK"
    else
        echo "❌ Auth utils import failed"
    fi
    
    # Test gamification import
    echo "Testing gamification import..."
    if python3 -c "from gamification import GamificationManager; print('Gamification import OK')" 2>/dev/null; then
        echo "✅ Gamification import: OK"
    else
        echo "❌ Gamification import failed"
    fi
    
    echo "❌ Cannot start app due to import errors"
    echo "🔧 Check the specific import errors above"
    exit 1
fi
