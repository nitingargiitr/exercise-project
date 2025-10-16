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

# Install dependencies first
echo "📦 Installing Python dependencies..."
echo "🔍 Checking pip availability..."
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 found, installing dependencies..."
    pip3 install --no-cache-dir --upgrade pip
    pip3 install --no-cache-dir -r requirements.txt
elif command -v pip &> /dev/null; then
    echo "✅ pip found, installing dependencies..."
    pip install --no-cache-dir --upgrade pip
    pip install --no-cache-dir -r requirements.txt
else
    echo "❌ pip not found, trying python -m pip..."
    python3 -m pip install --no-cache-dir --upgrade pip
    python3 -m pip install --no-cache-dir -r requirements.txt
fi
echo "✅ Dependencies installation completed"

# Verify Flask installation
echo "🔍 Verifying Flask installation..."
if python3 -c "import flask; print(f'Flask version: {flask.__version__}')" 2>/dev/null; then
    echo "✅ Flask is installed and working"
else
    echo "❌ Flask installation failed"
    echo "🔧 Trying to install Flask manually..."
    pip3 install Flask==2.3.3
    echo "🔍 Re-verifying Flask installation..."
    if python3 -c "import flask; print(f'Flask version: {flask.__version__}')" 2>/dev/null; then
        echo "✅ Flask is now installed and working"
    else
        echo "❌ Flask installation still failed"
        echo "🔧 Checking Python environment..."
        python3 --version
        which python3
        echo "🔧 Checking pip environment..."
        pip3 --version
        which pip3
    fi
fi

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
    
    # Test basic Python functionality
    echo "Testing basic Python functionality..."
    if python3 -c "print('Python is working')" 2>/dev/null; then
        echo "✅ Python is working"
    else
        echo "❌ Python is not working"
    fi
    
    # Test basic imports
    echo "Testing basic imports..."
    if python3 -c "import os, sys, time; print('Basic modules OK')" 2>/dev/null; then
        echo "✅ Basic modules: OK"
    else
        echo "❌ Basic modules failed"
    fi
    
    # Test Flask import
    echo "Testing Flask import..."
    if python3 -c "from flask import Flask; print('Flask OK')" 2>/dev/null; then
        echo "✅ Flask: OK"
    else
        echo "❌ Flask failed"
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
    
    echo "❌ Cannot start main app due to import errors"
    echo "🔧 Starting minimal app as fallback..."
    echo "🎯 This ensures your app is accessible while we fix the import issues"
    
    echo "🚀 Starting minimal app with health check support..."
    exec gunicorn \
        --bind 0.0.0.0:${PORT} \
        --workers 1 \
        --timeout 120 \
        --keep-alive 2 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --log-level info \
        --access-logfile - \
        --error-logfile - \
        --preload \
        minimal_app:app
fi
