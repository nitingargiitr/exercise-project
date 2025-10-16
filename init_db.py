#!/usr/bin/env python3
"""
Database initialization script for deployment
Run this script to create all database tables and initialize data
"""

import os
import sys
from app import app, db
from models import *
from gamification import initialize_gamification_data

def init_database():
    """Initialize the database with all tables and initial data"""
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Initialize gamification data
            print("Initializing gamification data...")
            initialize_gamification_data()
            print("✅ Gamification data initialized!")
            
            # Check if we have any users
            user_count = User.query.count()
            print(f"📊 Current users in database: {user_count}")
            
            print("\n🎉 Database initialization completed successfully!")
            print("Your app is ready for deployment!")
            
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    print("🚀 Initializing Exercise Analyzer Database...")
    print("=" * 50)
    init_database()
