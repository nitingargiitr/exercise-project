import os
import secrets
import hashlib
import requests
from datetime import datetime, timedelta
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, UserSession, db

class AuthManager:
    @staticmethod
    def hash_password(password):
        """Hash a password for storing"""
        return generate_password_hash(password)
    
    @staticmethod
    def check_password(stored_password, provided_password):
        """Check if a provided password matches the stored hash"""
        return check_password_hash(stored_password, provided_password)
    
    @staticmethod
    def create_user(email, password=None, name=None, google_id=None, profile_picture=None):
        """Create a new user"""
        try:
            user = User(
                email=email,
                password_hash=AuthManager.hash_password(password) if password else None,
                name=name or email.split('@')[0],
                google_id=google_id,
                profile_picture=profile_picture
            )
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password"""
        user = User.query.filter_by(email=email).first()
        if user and user.password_hash and AuthManager.check_password(user.password_hash, password):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        return None
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_user_by_google_id(google_id):
        """Get user by Google ID"""
        return User.query.filter_by(google_id=google_id).first()
    
    @staticmethod
    def create_session(user_id, remember_me=False):
        """Create a new session for user"""
        # Generate secure session token
        session_token = secrets.token_urlsafe(32)
        
        # Set expiration time
        if remember_me:
            expires_at = datetime.utcnow() + timedelta(days=30)  # 30 days for remember me
        else:
            expires_at = datetime.utcnow() + timedelta(hours=24)  # 24 hours for normal session
        
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at
        )
        
        db.session.add(session)
        db.session.commit()
        
        return session_token
    
    @staticmethod
    def validate_session(session_token):
        """Validate session token and return user"""
        session = UserSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
        
        if not session:
            return None
        
        # Check if session is expired
        if datetime.utcnow() > session.expires_at:
            session.is_active = False
            db.session.commit()
            return None
        
        return session.user
    
    @staticmethod
    def logout_session(session_token):
        """Logout user by deactivating session"""
        session = UserSession.query.filter_by(session_token=session_token).first()
        if session:
            session.is_active = False
            db.session.commit()
    
    @staticmethod
    def logout_all_sessions(user_id):
        """Logout all sessions for a user"""
        UserSession.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
        db.session.commit()

class GoogleOAuth:
    @staticmethod
    def get_google_user_info(access_token):
        """Get user info from Google using access token"""
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting Google user info: {e}")
            return None
    
    @staticmethod
    def exchange_code_for_token(code, redirect_uri):
        """Exchange authorization code for access token"""
        try:
            data = {
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            
            response = requests.post('https://oauth2.googleapis.com/token', data=data)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None
    
    @staticmethod
    def get_google_auth_url(redirect_uri):
        """Generate Google OAuth URL"""
        base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        params = {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', 'your-google-client-id'),
            'redirect_uri': redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'offline'
        }
        
        param_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f'{base_url}?{param_string}'
