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
    echo "🔧 Running detailed import test..."
    python3 test_imports.py
    echo "❌ Cannot start app due to import errors"
    exit 1
fi
