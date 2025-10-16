#!/usr/bin/env python3
"""
Simple health check server that starts immediately
This ensures health checks pass while dependencies are being installed
"""
import os
import sys
from flask import Flask

# Create minimal Flask app for health checks
app = Flask(__name__)

@app.route('/ping')
def ping():
    return "pong", 200

@app.route('/health')
def health():
    return "healthy", 200

@app.route('/status')
def status():
    return "ok", 200

@app.route('/healthcheck')
def healthcheck():
    return "ok", 200

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Exercise Analyzer - Starting Up</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 20px auto; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .status { color: #28a745; font-size: 18px; margin: 20px 0; }
            .info { color: #666; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏋️ Exercise Form Analyzer</h1>
            <div class="spinner"></div>
            <div class="status">🚀 Starting up...</div>
            <div class="info">Installing dependencies and initializing the application.</div>
            <div class="info">This may take a few moments. Please wait...</div>
        </div>
    </body>
    </html>
    """, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🏥 Starting health check server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
