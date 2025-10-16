#!/usr/bin/env python3
"""
Fallback Flask app for Railway deployment
This ensures the app always starts even if main app has issues
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Exercise Analyzer - Starting Up</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .container { max-width: 600px; margin: 0 auto; }
            .status { color: #28a745; font-size: 18px; margin: 20px 0; }
            .info { color: #666; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏋️ Exercise Form Analyzer</h1>
            <div class="status">✅ App is running!</div>
            <div class="info">The main application is starting up...</div>
            <div class="info">Please wait a moment and refresh the page.</div>
            <div class="info">If you continue to see this message, there may be an issue with the main app.</div>
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
        'status': 'fallback_app',
        'message': 'Main app is not available, using fallback',
        'timestamp': str(os.environ.get('TIMESTAMP', 'unknown'))
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting fallback app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
