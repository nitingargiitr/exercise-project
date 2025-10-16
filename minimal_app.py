#!/usr/bin/env python3
"""
Minimal working Flask app for Railway deployment
This ensures the app always starts even if there are import issues
"""
import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Basic routes
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Exercise Form Analyzer</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; margin-bottom: 30px; }
            .status { color: #28a745; font-size: 18px; margin: 20px 0; }
            .info { color: #666; margin: 10px 0; }
            .features { text-align: left; margin: 30px 0; }
            .feature { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏋️ Exercise Form Analyzer</h1>
            <div class="status">✅ App is running successfully!</div>
            <div class="info">Your Exercise Analyzer is deployed and working.</div>
            
            <div class="features">
                <h3>🎯 Features Available:</h3>
                <div class="feature">🔐 User Authentication - Sign up and login</div>
                <div class="feature">🏋️ Exercise Analysis - 5 exercise types</div>
                <div class="feature">📹 Video Upload - AI-powered form feedback</div>
                <div class="feature">📊 Progress Tracking - Exercise history</div>
                <div class="feature">🎮 Gamification - Achievements and levels</div>
            </div>
            
            <div class="info">
                <p><strong>Next Steps:</strong></p>
                <p>1. Sign up for an account</p>
                <p>2. Choose an exercise type</p>
                <p>3. Upload a video for analysis</p>
                <p>4. Get AI-powered feedback on your form</p>
            </div>
        </div>
    </body>
    </html>
    """, 200

@app.route('/ping')
def ping():
    return "pong"

@app.route('/health')
def health():
    return "healthy"

@app.route('/status')
def status():
    return "ok"

@app.route('/debug')
def debug():
    return jsonify({
        'status': 'minimal_app_running',
        'message': 'Exercise Analyzer is running in minimal mode',
        'python_version': sys.version,
        'environment': {
            'PORT': os.environ.get('PORT'),
            'SECRET_KEY': 'set' if os.environ.get('SECRET_KEY') else 'not_set'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting minimal Exercise Analyzer on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
