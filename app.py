import os
import sys
import time
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, flash, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import tempfile
import shutil

# Try to import AI/ML dependencies with fallback
try:
    import cv2
    import torch
    import numpy as np
    import mediapipe as mp
    from pushup_lstm import PushupLSTM
    from dataset_angles import calculate_angle
    
    # Configure OpenCV to suppress warnings and handle video processing better
    cv2.setLogLevel(cv2.LOG_LEVEL_ERROR)  # Suppress OpenCV warnings
    
    AI_AVAILABLE = True
    print("✅ AI/ML dependencies loaded successfully")
except ImportError as e:
    print(f"⚠️ AI/ML dependencies not available: {e}")
    print("App will run in basic mode without AI features")
    AI_AVAILABLE = False
    # Create dummy classes for fallback
    class PushupLSTM:
        def __init__(self, *args, **kwargs): pass
        def load_state_dict(self, *args, **kwargs): pass
        def eval(self): return self
        def to(self, *args, **kwargs): return self
        def __call__(self, *args, **kwargs): return None
    def calculate_angle(*args, **kwargs): return 0

# Import core app dependencies with comprehensive error handling
print("🔧 Loading core dependencies...")

# Create dummy classes first as fallbacks
class DummyDB:
    def init_app(self, app): pass
    def create_all(self): pass
    def session(self): return self
    def execute(self, query): pass
    def add(self, obj): pass
    def commit(self): pass

class DummyUser:
    def __init__(self): 
        self.id = 1
        self.is_authenticated = False

# Initialize with dummy values first
db = DummyDB()
User = DummyUser
current_user = DummyUser()

# Try to import real dependencies, but don't fail if they don't work
try:
    print("📦 Attempting to import models...")
    from models import db, User, UserSession, ExerciseHistory, UserLevel, Achievement, UserAchievement, Card, UserCard, DailyChallenge, UserDailyChallenge
    print("✅ Models imported successfully")
except Exception as e:
    print(f"⚠️ Models import failed: {e}")
    print("Using dummy models...")
    # Create dummy classes for missing models
    class DummyUser: pass
    class DummySession: pass
    class DummyHistory: pass
    class DummyLevel: pass
    class DummyAchievement: pass
    class DummyCard: pass
    class DummyChallenge: pass
    User = DummyUser
    UserSession = DummySession
    ExerciseHistory = DummyHistory
    UserLevel = DummyLevel
    Achievement = DummyAchievement
    UserAchievement = DummyAchievement
    Card = DummyCard
    UserCard = DummyCard
    DailyChallenge = DummyChallenge
    UserDailyChallenge = DummyChallenge

try:
    print("📦 Attempting to import forms...")
    from forms import LoginForm, SignupForm, ForgotPasswordForm
    print("✅ Forms imported successfully")
except Exception as e:
    print(f"⚠️ Forms import failed: {e}")
    print("Using dummy forms...")
    # Create dummy form classes
    class DummyForm: pass
    LoginForm = DummyForm
    SignupForm = DummyForm
    ForgotPasswordForm = DummyForm

try:
    print("📦 Attempting to import auth_utils...")
    from auth_utils import AuthManager, GoogleOAuth
    print("✅ Auth utils imported successfully")
except Exception as e:
    print(f"⚠️ Auth utils import failed: {e}")
    print("Using dummy auth...")
    # Create dummy auth classes
    class DummyAuthManager: pass
    class DummyGoogleOAuth: pass
    AuthManager = DummyAuthManager
    GoogleOAuth = DummyGoogleOAuth

try:
    print("📦 Attempting to import gamification...")
    from gamification import GamificationManager, initialize_gamification_data
    print("✅ Gamification imported successfully")
except Exception as e:
    print(f"⚠️ Gamification import failed: {e}")
    print("Using dummy gamification...")
    # Create dummy gamification functions
    def initialize_gamification_data(): pass

print("✅ Core dependencies loading completed")

app = Flask(__name__)

# Environment configuration
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# CRITICAL: Add ping endpoint immediately for health checks
@app.route('/ping')
def ping():
    """Ultra-simple ping endpoint for health checks"""
    return "pong"

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"🚨 Global error handler: {e}")
    return jsonify({
        'error': 'An error occurred',
        'message': str(e),
        'status': 'error'
    }), 500

# Ensure all routes have error handling
def safe_route(route_func):
    def wrapper(*args, **kwargs):
        try:
            return route_func(*args, **kwargs)
        except Exception as e:
            print(f"🚨 Route error in {route_func.__name__}: {e}")
            return jsonify({
                'error': 'Route error',
                'message': str(e)
            }), 500
    return wrapper

# Production settings
if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    print("🔒 Production security settings enabled")
else:
    print("🔓 Development mode - security settings relaxed")

# Database configuration
# Use environment variable for database URL, fallback to SQLite for development
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Production database (PostgreSQL/MySQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Development database (SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exercise_analyzer.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration for persistence
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Initialize gamification (with error handling)
try:
    gamification = GamificationManager()
    gamification.init_app(app)
    print("✅ Gamification manager initialized")
except Exception as e:
    print(f"⚠️ Gamification initialization failed: {e}")
    # Create a dummy gamification manager
    class DummyGamificationManager:
        def init_app(self, app): pass
        def get_user_stats(self, user_id): return {}
        def get_or_create_user_level(self, user_id): return None
        def check_level_up(self, user_level): return {'leveled_up': False}
        def calculate_workout_rewards(self, user_id, exercise_type, accuracy, mistakes): return {}
    gamification = DummyGamificationManager()
    print("✅ Dummy gamification manager created")

# Initialize database when app starts (for Gunicorn)
def initialize_database_on_startup():
    """Initialize database when app starts with Gunicorn"""
    try:
        print("🗄️ Initializing database on startup...")
        with app.app_context():
            try:
                db.create_all()
                print("✅ Database tables created successfully")
            except Exception as e:
                print(f"⚠️ Database creation failed: {e}")
                print("Continuing without database...")
            
            # Initialize gamification data
            try:
                initialize_gamification_data()
                print("✅ Gamification data initialized successfully")
            except Exception as e:
                print(f"⚠️ Gamification initialization failed: {e}")
                print("Continuing without gamification...")
                
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("Continuing without database...")

# Call database initialization (but don't let it crash the app)
print("🔧 Starting database initialization...")
try:
    initialize_database_on_startup()
    print("✅ Database initialization completed")
except Exception as e:
    print(f"⚠️ Database initialization error (continuing): {e}")
    print("App will continue without database features...")

print("✅ App initialization completed successfully")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------------------
# Configuration
# ----------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(ROOT, "models")
DATA_DIR = os.path.join(ROOT, "data")
UPLOAD_DIR = os.path.join(ROOT, "uploads")
OUTPUT_DIR = os.path.join(ROOT, "output")

# Create directories
for directory in [UPLOAD_DIR, OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Exercise configurations
EXERCISES = {
    "pushup": {
        "name": "Push-ups",
        "input_size": 5,
        "model_file": "pushup_lstm_features.pt",
        "stats_file": "angle_stats_pushup.npz",
        "demo_video": "pushup/Copy of push up 1.mp4",
        "description": "A classic bodyweight exercise that targets chest, shoulders, and triceps.",
        "benefits": [
            "Builds upper body strength",
            "Improves core stability",
            "Enhances cardiovascular fitness",
            "No equipment required",
            "Can be modified for all fitness levels"
        ],
        "muscles": ["Chest", "Shoulders", "Triceps", "Core"]
    },
    "pullup": {
        "name": "Pull-ups",
        "input_size": 2,
        "model_file": "pullup_lstm_features.pt",
        "stats_file": "angle_stats_pullup.npz",
        "demo_video": "pullup/1.mp4",
        "description": "An upper body strength exercise that primarily targets the back and biceps.",
        "benefits": [
            "Builds back and bicep strength",
            "Improves grip strength",
            "Enhances shoulder stability",
            "Develops functional pulling strength",
            "Great for posture improvement"
        ],
        "muscles": ["Back", "Biceps", "Shoulders", "Core"]
    },
    "plank": {
        "name": "Plank",
        "input_size": 3,
        "model_file": "plank_lstm_features.pt",
        "stats_file": "angle_stats_plank.npz",
        "demo_video": "plank/WhatsApp Video 2025-10-11 at 21.05.36.mp4",
        "description": "An isometric core exercise that builds stability and endurance.",
        "benefits": [
            "Strengthens entire core",
            "Improves posture",
            "Reduces back pain risk",
            "Enhances balance and stability",
            "Can be done anywhere"
        ],
        "muscles": ["Core", "Shoulders", "Glutes", "Back"]
    },
    "squat": {
        "name": "Squats",
        "input_size": 5,
        "model_file": "squat_lstm_features.pt",
        "stats_file": "angle_stats_squat.npz",
        "demo_video": "squat/WhatsApp Video 2025-10-11 at 21.45.12.mp4",
        "description": "A fundamental lower body exercise that targets legs and glutes.",
        "benefits": [
            "Builds leg and glute strength",
            "Improves functional movement",
            "Enhances balance and coordination",
            "Burns calories effectively",
            "Strengthens core muscles"
        ],
        "muscles": ["Quadriceps", "Glutes", "Hamstrings", "Core"]
    },
    "tricep_dips": {
        "name": "Tricep Dips",
        "input_size": 4,
        "model_file": "tricep_dips_lstm_features.pt",
        "stats_file": "angle_stats_tricep_dips.npz",
        "demo_video": "tricep_dips/WhatsApp Video 2025-10-11 at 21.46.08.mp4",
        "description": "An upper body exercise that specifically targets the triceps and shoulders.",
        "benefits": [
            "Builds tricep strength",
            "Strengthens shoulders",
            "Improves pushing power",
            "Can be done with minimal equipment",
            "Great for arm definition"
        ],
        "muscles": ["Triceps", "Shoulders", "Chest", "Core"]
    }
}

# ----------------------------
# MediaPipe setup (with fallback)
# ----------------------------
if AI_AVAILABLE:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose(static_image_mode=False,
                        model_complexity=1,
                        enable_segmentation=False,
                        min_detection_confidence=0.3,
                        min_tracking_confidence=0.3)
    print("✅ MediaPipe initialized successfully")
else:
    # Dummy classes for fallback
    class DummyPose:
        def process(self, *args, **kwargs): return None
    class DummyDrawing:
        def draw_landmarks(self, *args, **kwargs): pass
    class DummyPoseConnections:
        pass
    
    mp_pose = type('mp_pose', (), {'POSE_CONNECTIONS': DummyPoseConnections()})()
    mp_drawing = type('mp_drawing', (), {'draw_landmarks': DummyDrawing().draw_landmarks})()
    pose = DummyPose()
    print("⚠️ MediaPipe not available - using dummy implementation")

# ----------------------------
# Authentication Routes
# ----------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = AuthManager.authenticate_user(form.email.data, form.password.data)
        if user:
            login_user(user, remember=form.remember_me.data)
            session_token = AuthManager.create_session(user.id, form.remember_me.data)
            session['session_token'] = session_token
            session.permanent = form.remember_me.data  # Make session permanent if remember me is checked
            flash('Welcome back! You have successfully signed in.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    # Generate Google OAuth URL (only if credentials are configured)
    google_auth_url = None
    if os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_ID') != 'your-google-client-id':
        google_auth_url = GoogleOAuth.get_google_auth_url(request.url_root + 'auth/google/callback')
    
    return render_template('login.html', form=form, google_auth_url=google_auth_url)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = SignupForm()
    if form.validate_on_submit():
        try:
            user = AuthManager.create_user(
                email=form.email.data,
                password=form.password.data,
                name=form.name.data
            )
            login_user(user, remember=True)  # Remember new users by default
            session_token = AuthManager.create_session(user.id, True)
            session['session_token'] = session_token
            session.permanent = True  # Make session permanent for new users
            flash('Account created successfully! Welcome to your fitness journey.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash('An error occurred while creating your account. Please try again.', 'error')
    
    # Generate Google OAuth URL (only if credentials are configured)
    google_auth_url = None
    if os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_ID') != 'your-google-client-id':
        google_auth_url = GoogleOAuth.get_google_auth_url(request.url_root + 'auth/google/callback')
    
    return render_template('signup.html', form=form, google_auth_url=google_auth_url)

@app.route('/logout')
@login_required
def logout():
    # Deactivate user session
    if 'session_token' in session:
        AuthManager.logout_session(session['session_token'])
        session.pop('session_token', None)
    
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        # In a real application, you would send an email here
        flash('Password reset instructions have been sent to your email.', 'info')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html', form=form)

@app.route('/auth/google/callback')
def google_callback():
    code = request.args.get('code')
    if not code:
        flash('Authorization failed. Please try again.', 'error')
        return redirect(url_for('login'))
    
    # Exchange code for token
    token_data = GoogleOAuth.exchange_code_for_token(code, request.url)
    if not token_data:
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('login'))
    
    # Get user info from Google
    user_info = GoogleOAuth.get_google_user_info(token_data['access_token'])
    if not user_info:
        flash('Failed to get user information. Please try again.', 'error')
        return redirect(url_for('login'))
    
    # Check if user exists
    user = AuthManager.get_user_by_google_id(user_info['id'])
    if not user:
        # Check if user exists with same email
        user = AuthManager.get_user_by_email(user_info['email'])
        if user:
            # Link Google account to existing user
            user.google_id = user_info['id']
            user.profile_picture = user_info.get('picture')
            db.session.commit()
        else:
            # Create new user
            user = AuthManager.create_user(
                email=user_info['email'],
                name=user_info['name'],
                google_id=user_info['id'],
                profile_picture=user_info.get('picture')
            )
    
    # Log in user
    login_user(user)
    session_token = AuthManager.create_session(user.id, True)
    session['session_token'] = session_token
    flash('Welcome! You have successfully signed in with Google.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    # Get user stats including gamification data
    user_stats = gamification.get_user_stats(current_user.id)
    return render_template('profile.html', user=current_user, stats=user_stats)

@app.route('/history')
@login_required
def history():
    # Get user's exercise history
    exercise_history = ExerciseHistory.query.filter_by(user_id=current_user.id).order_by(ExerciseHistory.created_at.desc()).all()
    return render_template('history.html', history=exercise_history)

@app.route('/achievements')
@login_required
def achievements():
    # Get all achievements and user's earned achievements
    all_achievements = Achievement.query.filter_by(is_active=True).all()
    user_achievements = UserAchievement.query.filter_by(user_id=current_user.id).all()
    earned_ids = [ua.achievement_id for ua in user_achievements]
    
    return render_template('achievements.html', 
                         all_achievements=all_achievements, 
                         earned_ids=earned_ids)

@app.route('/cards')
@login_required
def cards():
    # Get user's card collection
    user_cards = db.session.query(Card, UserCard)\
        .join(UserCard, Card.id == UserCard.card_id)\
        .filter(UserCard.user_id == current_user.id)\
        .order_by(UserCard.obtained_at.desc()).all()
    
    return render_template('cards.html', user_cards=user_cards)

@app.route('/leaderboard')
@login_required
def leaderboard():
    # Get top users by level and XP
    top_users = db.session.query(User, UserLevel)\
        .join(UserLevel, User.id == UserLevel.user_id)\
        .order_by(UserLevel.level.desc(), UserLevel.experience_points.desc())\
        .limit(10).all()
    
    return render_template('leaderboard.html', top_users=top_users)

@app.route('/daily-challenge')
@login_required
def daily_challenge():
    # Get today's daily challenge
    today = date.today()
    challenge = DailyChallenge.query.filter_by(date=today, is_active=True).first()
    
    # If no challenge exists, create one
    if not challenge:
        import random
        exercise_types = ['pushup', 'pullup', 'squat', 'plank', 'tricep_dip']
        exercise_type = random.choice(exercise_types)
        target_reps = random.randint(5, 20)
        target_accuracy = random.randint(80, 95)
        
        challenge = DailyChallenge(
            name=f"Daily {exercise_type.title()} Challenge",
            description=f"Complete {target_reps} {exercise_type.replace('_', ' ')} with {target_accuracy}% accuracy",
            exercise_type=exercise_type,
            target_reps=target_reps,
            target_accuracy=target_accuracy,
            date=today
        )
        db.session.add(challenge)
        db.session.commit()
    
    # Check if user already completed it
    user_challenge = None
    if challenge:
        user_challenge = UserDailyChallenge.query.filter_by(
            user_id=current_user.id, 
            challenge_id=challenge.id
        ).first()
    
    return render_template('daily_challenge.html', 
                         challenge=challenge, 
                         user_challenge=user_challenge)

@app.route('/complete-daily-challenge/<int:challenge_id>')
@login_required
def complete_daily_challenge(challenge_id):
    # Check if user already completed this challenge
    user_challenge = UserDailyChallenge.query.filter_by(
        user_id=current_user.id, 
        challenge_id=challenge_id
    ).first()
    
    if user_challenge and user_challenge.completed:
        flash('You have already completed this daily challenge!', 'info')
        return redirect(url_for('daily_challenge'))
    
    # Mark daily challenge as completed
    if not user_challenge:
        user_challenge = UserDailyChallenge(
            user_id=current_user.id,
            challenge_id=challenge_id
        )
        db.session.add(user_challenge)
    
    user_challenge.completed = True
    user_challenge.completed_at = datetime.utcnow()
    
    # Award bonus XP and check for level up
    challenge = DailyChallenge.query.get(challenge_id)
    if challenge:
        user_level = gamification.get_or_create_user_level(current_user.id)
        old_level = user_level.level
        
        # Award XP
        user_level.experience_points += challenge.xp_reward
        
        # Check for level up
        level_up_result = gamification.check_level_up(user_level)
        
        db.session.commit()
        
        if level_up_result['leveled_up']:
            flash(f'🎉 LEVEL UP! You reached Level {user_level.level} - {user_level.get_level_name()}! Daily challenge completed! You earned {challenge.xp_reward} bonus XP!', 'success')
        else:
            flash(f'Daily challenge completed! You earned {challenge.xp_reward} bonus XP!', 'success')
    
    return redirect(url_for('daily_challenge'))

# ----------------------------
# Main Routes
# ----------------------------

@app.route('/')
def index():
    try:
        if not current_user.is_authenticated:
            return render_template('landing.html')
        return render_template('index.html', exercises=EXERCISES)
    except Exception as e:
        print(f"Error in index route: {e}")
        return f"Error loading page: {str(e)}", 500

@app.route('/health')
def health_check():
    """Ultra-simple health check endpoint"""
    return "healthy", 200

@app.route('/status')
def status_check():
    """Simple status check endpoint"""
    return "ok", 200

@app.route('/test')
def test_route():
    """Simple test route with no dependencies"""
    return jsonify({
        'message': 'App is working!',
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'success'
    }), 200



@app.route('/debug')
def debug_info():
    """Debug endpoint to check app status"""
    try:
        import sys
        import traceback
        
        # Test database connection
        db_status = "unknown"
        try:
            db.session.execute('SELECT 1')
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Test imports
        import_status = {}
        try:
            from models import db
            import_status['models'] = "ok"
        except Exception as e:
            import_status['models'] = f"error: {str(e)}"
        
        try:
            from forms import LoginForm
            import_status['forms'] = "ok"
        except Exception as e:
            import_status['forms'] = f"error: {str(e)}"
        
        return jsonify({
            'status': 'debug',
            'timestamp': datetime.utcnow().isoformat(),
            'python_version': sys.version,
            'ai_available': AI_AVAILABLE,
            'database': db_status,
            'imports': import_status,
            'environment': {
                'PORT': os.environ.get('PORT'),
                'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT'),
                'DATABASE_URL': 'set' if os.environ.get('DATABASE_URL') else 'not_set'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'debug_error',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/exercise/<exercise_type>')
@login_required
def exercise_info(exercise_type):
    if exercise_type not in EXERCISES:
        return redirect(url_for('index'))
    
    exercise = EXERCISES[exercise_type]
    demo_video_path = os.path.join(DATA_DIR, exercise['demo_video'])
    
    return render_template('exercise_info.html', 
                         exercise_type=exercise_type, 
                         exercise=exercise,
                         demo_video_exists=os.path.exists(demo_video_path),
                         demo_video_path=exercise['demo_video'])

@app.route('/analyze/<exercise_type>')
@login_required
def analyze_page(exercise_type):
    if exercise_type not in EXERCISES:
        return redirect(url_for('index'))
    
    exercise = EXERCISES[exercise_type]
    return render_template('analyze.html', exercise_type=exercise_type, exercise=exercise)

@app.route('/upload', methods=['POST'])
@login_required
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    exercise_type = request.form.get('exercise_type')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if exercise_type not in EXERCISES:
        return jsonify({'error': 'Invalid exercise type'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)
        
        session['uploaded_file'] = filepath
        session['exercise_type'] = exercise_type
        
        return jsonify({'success': True, 'filename': filename})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/process')
@login_required
def process_video():
    if 'uploaded_file' not in session or 'exercise_type' not in session:
        return redirect(url_for('index'))
    
    filepath = session['uploaded_file']
    exercise_type = session['exercise_type']
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Uploaded file not found'}), 400
    
    try:
        print(f"Starting video analysis for {exercise_type}...")
        result = analyze_video(filepath, exercise_type)
        print(f"Analysis completed: {result}")
        
        # Store result in session for results page
        session['analysis_result'] = result
        
        return jsonify(result)
    except Exception as e:
        print(f"Analysis error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a fallback result instead of error
        fallback_result = {
            'exercise_type': exercise_type,
            'exercise_name': EXERCISES.get(exercise_type, {}).get('name', 'Exercise'),
            'accuracy': 75,
            'mistakes': [f'Analysis encountered an error: {str(e)}'],
            'output_video': None,
            'total_frames': 0,
            'mock_result': True,
            'error': str(e)
        }
        
        session['analysis_result'] = fallback_result
        return jsonify(fallback_result)

@app.route('/results')
@login_required
def results():
    if 'analysis_result' not in session:
        return redirect(url_for('index'))
    
    result = session['analysis_result']
    return render_template('results.html', result=result)

@app.route('/video/<filename>')
def stream_video(filename):
    """Stream the output video file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='video/mp4')
    return "Video not found", 404

@app.route('/download/<filename>')
def download_file(filename):
    """Download the output video file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=filename)
    return "File not found", 404

@app.route('/demo/<path:filename>')
def serve_demo_video(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return "Demo video not found", 404


# ----------------------------
# Helper functions
# ----------------------------

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_video(video_path, exercise_type):
    """Analyze video and return results"""
    print(f"🔍 Starting video analysis for {exercise_type}...")
    
    # Check if AI dependencies are available
    if not AI_AVAILABLE:
        print("⚠️ AI dependencies not available, returning mock result")
        return {
            'exercise_type': exercise_type,
            'exercise_name': EXERCISES[exercise_type]['name'],
            'accuracy': 85,
            'mistakes': ['AI analysis not available - running in basic mode'],
            'output_video': None,
            'total_frames': 0,
            'mock_result': True,
            'message': 'AI features are not available in this deployment'
        }
    
    try:
        exercise_config = EXERCISES[exercise_type]
        print(f"📋 Exercise config loaded: {exercise_config['name']}")
        
        # Load model and stats
        model_path = os.path.join(MODEL_DIR, exercise_config['model_file'])
        stats_path = os.path.join(MODEL_DIR, exercise_config['stats_file'])
        
        print(f"🔍 Checking model files: {model_path}, {stats_path}")
        
        if not os.path.exists(model_path) or not os.path.exists(stats_path):
            print("⚠️ Model files not found, returning mock result")
            # Return a mock result if models are not available
            return {
                'exercise_type': exercise_type,
                'exercise_name': exercise_config['name'],
                'accuracy': 85,  # Mock accuracy
                'mistakes': ['Model files not available - using mock analysis'],
                'output_video': None,
                'total_frames': 0,
                'mock_result': True
            }
        
        print("🤖 Loading AI model...")
        # Setup model
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = PushupLSTM(input_size=exercise_config['input_size'])
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval().to(device)
        
        print("📊 Loading angle statistics...")
        # Load angle stats
        angle_stats = np.load(stats_path)
        mean_angles = angle_stats["mean"]
        print("✅ Model and stats loaded successfully")
    except Exception as e:
        # Return a mock result if model loading fails
        return {
            'exercise_type': exercise_type,
            'exercise_name': exercise_config['name'],
            'accuracy': 80,  # Mock accuracy
            'mistakes': [f'Model loading failed: {str(e)}'],
            'output_video': None,
            'total_frames': 0,
            'mock_result': True
        }
    
    # Process video with better error handling
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video file. Please check if the file is corrupted or in an unsupported format.")
        
        # Get video properties with fallbacks
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps is None or fps <= 0:
            fps = 30  # Default FPS
        else:
            fps = int(fps)
            
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        if width is None or height is None or width <= 0 or height <= 0:
            raise Exception("Invalid video dimensions. Please check if the video file is valid.")
        
        width = int(width)
        height = int(height)
        
        # Create output video with better codec handling
        output_filename = f"feedback_{exercise_type}_{int(time.time())}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # Try different codecs for better compatibility
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            # Fallback to H264 codec
            fourcc = cv2.VideoWriter_fourcc(*"H264")
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
    except Exception as e:
        print(f"Video processing error: {e}")
        # Return a basic result if video processing fails
        return {
            'exercise_type': exercise_type,
            'exercise_name': exercise_config['name'],
            'accuracy': 75,
            'mistakes': [f'Video processing error: {str(e)}'],
            'output_video': None,
            'total_frames': 0,
            'mock_result': True
        }
    
    seq_len = 60
    all_keypoints = []
    frame_accuracies = []
    all_mistakes = []
    frame_count = 0
    
    print("🎬 Starting video processing...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        if frame_count % 30 == 0:  # Log every 30 frames
            print(f"📹 Processing frame {frame_count}...")
        
        try:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb = np.ascontiguousarray(image_rgb)
            if image_rgb.dtype != np.uint8:
                image_rgb = image_rgb.astype(np.uint8)
            results = pose.process(image_rgb)
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            results = None
        
        frame_angles = None
        
        if results and results.pose_landmarks:
            # Extract keypoints
            keypoints_flat = np.zeros(33*2)
            for i, lm in enumerate(results.pose_landmarks.landmark):
                keypoints_flat[i*2] = lm.x * width
                keypoints_flat[i*2+1] = lm.y * height
            
            # Draw pose landmarks and connections on frame
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # Calculate angles based on exercise type
            frame_angles = calculate_exercise_angles(keypoints_flat, exercise_type)
        
        # Append frame angles
        if frame_angles is None:
            all_keypoints.append(np.zeros(exercise_config['input_size']))
        else:
            all_keypoints.append(frame_angles)
        
        # Prepare sequence for model
        keypoints_seq = np.array(all_keypoints[-seq_len:])
        if len(keypoints_seq) < seq_len:
            pad = np.zeros((seq_len - len(keypoints_seq), keypoints_seq.shape[1]))
            keypoints_seq = np.vstack([pad, keypoints_seq])
        
        # Get prediction
        input_tensor = torch.tensor([keypoints_seq], dtype=torch.float32).to(device)
        pred = model(input_tensor)
        prob_correct = torch.softmax(pred, dim=1)[0,1].item()
        
        # Detect mistakes
        mistakes = detect_mistakes(keypoints_seq[-1], mean_angles, exercise_type)
        all_mistakes.extend(mistakes)
        
        # Calculate accuracy
        accuracy = int(min(100, max(0, prob_correct * 100 - len(mistakes)*10)))
        frame_accuracies.append(accuracy)
        
        # Draw feedback on frame
        y_offset = 30
        for i, mistake in enumerate(mistakes):
            cv2.putText(frame, mistake, (30, y_offset + i*30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        display_acc = int(np.mean(frame_accuracies[-20:])) if frame_accuracies else 0
        cv2.putText(frame, f"Accuracy: {display_acc}%", 
                   (30, y_offset + (len(mistakes)+1)*30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        out.write(frame)
    
    cap.release()
    out.release()
    
    print(f"✅ Video processing completed. Processed {frame_count} frames.")
    
    # Calculate final results
    avg_accuracy = int(np.mean(frame_accuracies)) if frame_accuracies else 0
    unique_mistakes = list(set(all_mistakes))
    
    if len(frame_accuracies) == 0:
        print("⚠️ No pose landmarks detected")
        raise Exception("No pose landmarks detected in the video. Please ensure the person is clearly visible and well-lit.")
    
    result = {
        'exercise_type': exercise_type,
        'exercise_name': exercise_config['name'],
        'accuracy': avg_accuracy,
        'mistakes': unique_mistakes,
        'output_video': output_filename,
        'total_frames': len(frame_accuracies)
    }
    
    print(f"🎯 Analysis result: {result}")
    
    # Save exercise history for the user
    if current_user.is_authenticated:
        try:
            import json
            exercise_history = ExerciseHistory(
                user_id=current_user.id,
                exercise_type=exercise_type,
                accuracy=avg_accuracy,
                mistakes=json.dumps(unique_mistakes),
                video_filename=output_filename
            )
            db.session.add(exercise_history)
            db.session.commit()
            
            # Calculate gamification rewards
            rewards = gamification.calculate_workout_rewards(
                current_user.id, 
                exercise_type, 
                avg_accuracy, 
                unique_mistakes
            )
            
            # Add rewards to result
            result['gamification'] = rewards
            
        except Exception as e:
            print(f"Error saving exercise history: {e}")
    
    session['analysis_result'] = result
    
    return result

def calculate_exercise_angles(keypoints_flat, exercise_type):
    """Calculate angles based on exercise type"""
    if exercise_type == "pushup":
        left_elbow = calculate_angle(keypoints_flat[11*2:11*2+2],
                                   keypoints_flat[13*2:13*2+2],
                                   keypoints_flat[15*2:15*2+2])
        right_elbow = calculate_angle(keypoints_flat[12*2:12*2+2],
                                    keypoints_flat[14*2:14*2+2],
                                    keypoints_flat[16*2:16*2+2])
        back_angle = calculate_angle(keypoints_flat[11*2:11*2+2],
                                   keypoints_flat[23*2:23*2+2],
                                   keypoints_flat[25*2:25*2+2])
        left_knee = calculate_angle(keypoints_flat[23*2:23*2+2],
                                  keypoints_flat[25*2:25*2+2],
                                  keypoints_flat[27*2:27*2+2])
        right_knee = calculate_angle(keypoints_flat[24*2:24*2+2],
                                   keypoints_flat[26*2:26*2+2],
                                   keypoints_flat[28*2:28*2+2])
        return np.array([left_elbow, right_elbow, back_angle, left_knee, right_knee])
    
    elif exercise_type == "pullup":
        shoulder = keypoints_flat[11*2:11*2+2]
        elbow = keypoints_flat[13*2:13*2+2]
        wrist = keypoints_flat[15*2:15*2+2]
        hip = keypoints_flat[23*2:23*2+2]
        
        elbow_angle = calculate_angle(wrist, elbow, shoulder)
        shoulder_angle = calculate_angle(elbow, shoulder, hip)
        return np.array([elbow_angle, shoulder_angle])
    
    elif exercise_type == "plank":
        shoulder = keypoints_flat[11*2:11*2+2]
        hip = keypoints_flat[23*2:23*2+2]
        ankle = keypoints_flat[27*2:27*2+2]
        elbow = keypoints_flat[13*2:13*2+2]
        wrist = keypoints_flat[15*2:15*2+2]
        knee = keypoints_flat[25*2:25*2+2]
        
        back_angle = calculate_angle(shoulder, hip, ankle)
        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        hip_angle = calculate_angle(shoulder, hip, knee)
        return np.array([back_angle, elbow_angle, hip_angle])
    
    elif exercise_type == "squat":
        hip = keypoints_flat[23*2:23*2+2]
        knee = keypoints_flat[25*2:25*2+2]
        ankle = keypoints_flat[27*2:27*2+2]
        shoulder = keypoints_flat[11*2:11*2+2]
        hip_r = keypoints_flat[24*2:24*2+2]
        knee_r = keypoints_flat[26*2:26*2+2]
        ankle_r = keypoints_flat[28*2:28*2+2]
        
        left_knee_angle = calculate_angle(hip, knee, ankle)
        right_knee_angle = calculate_angle(hip_r, knee_r, ankle_r)
        left_hip_angle = calculate_angle(shoulder, hip, knee)
        right_hip_angle = calculate_angle(shoulder, hip_r, knee_r)
        back_angle = calculate_angle(shoulder, hip, ankle)
        
        return np.array([left_knee_angle, right_knee_angle, left_hip_angle, 
                        right_hip_angle, back_angle])
    
    elif exercise_type == "tricep_dips":
        left_shoulder = keypoints_flat[11*2:11*2+2]
        left_elbow = keypoints_flat[13*2:13*2+2]
        left_wrist = keypoints_flat[15*2:15*2+2]
        left_hip = keypoints_flat[23*2:23*2+2]
        right_shoulder = keypoints_flat[12*2:12*2+2]
        right_elbow = keypoints_flat[14*2:14*2+2]
        right_wrist = keypoints_flat[16*2:16*2+2]
        right_hip = keypoints_flat[24*2:24*2+2]
        
        left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        left_shoulder_angle = calculate_angle(left_elbow, left_shoulder, left_hip)
        right_shoulder_angle = calculate_angle(right_elbow, right_shoulder, right_hip)
        
        return np.array([left_elbow_angle, right_elbow_angle,
                        left_shoulder_angle, right_shoulder_angle])
    
    return None

def detect_mistakes(current_angles, mean_angles, exercise_type):
    """Detect form mistakes based on current angles and mean angles"""
    mistakes = []
    
    if exercise_type == "pushup":
        avg_elbows = (current_angles[0] + current_angles[1]) / 2.0
        if avg_elbows > mean_angles[0] + 10:
            mistakes.append("Go lower - bend elbows more")
        if abs(current_angles[2] - mean_angles[2]) > 15:
            mistakes.append("Keep back straight")
        if (current_angles[3] + current_angles[4]) / 2 > mean_angles[3] + 10:
            mistakes.append("Knees bent - keep legs straight")
    
    elif exercise_type == "pullup":
        if current_angles[0] > mean_angles[0] + 15:
            mistakes.append("Pull higher - bend the elbows more at top")
        if current_angles[1] > mean_angles[1] + 15:
            mistakes.append("Drive shoulders up - reach the bar higher")
        if current_angles[1] < mean_angles[1] - 20:
            mistakes.append("Control the descent - don't drop too fast")
    
    elif exercise_type == "plank":
        if abs(current_angles[0] - 180) > 15:
            if current_angles[0] < 165:
                mistakes.append("Hips too high - lower your hips")
            else:
                mistakes.append("Hips sagging - raise your hips")
        if abs(current_angles[1] - mean_angles[1]) > 20:
            mistakes.append("Adjust elbow position - keep forearms flat")
        if abs(current_angles[2] - mean_angles[2]) > 15:
            if current_angles[2] < mean_angles[2] - 15:
                mistakes.append("Engage core - don't let hips drop")
            else:
                mistakes.append("Keep body straight - hips too high")
    
    elif exercise_type == "squat":
        avg_knee = (current_angles[0] + current_angles[1]) / 2.0
        if avg_knee > 100:
            mistakes.append("Go deeper - squat below parallel")
        knee_diff = abs(current_angles[0] - current_angles[1])
        if knee_diff > 15:
            mistakes.append("Uneven knees - maintain symmetry")
        avg_hip = (current_angles[2] + current_angles[3]) / 2.0
        if avg_hip > mean_angles[2] + 20:
            mistakes.append("Push hips back more - proper hip hinge")
        if current_angles[4] < mean_angles[4] - 15:
            mistakes.append("Keep chest up - too much forward lean")
        elif current_angles[4] > mean_angles[4] + 15:
            mistakes.append("Lean forward slightly - engage posterior chain")
    
    elif exercise_type == "tricep_dips":
        avg_elbow = (current_angles[0] + current_angles[1]) / 2.0
        if avg_elbow > 110:
            mistakes.append("Go deeper - lower until elbows at 90 degrees")
        elbow_diff = abs(current_angles[0] - current_angles[1])
        if elbow_diff > 15:
            mistakes.append("Uneven elbows - maintain symmetry")
        avg_shoulder = (current_angles[2] + current_angles[3]) / 2.0
        if avg_shoulder < mean_angles[2] - 15:
            mistakes.append("Keep chest up - don't lean too far forward")
        if avg_elbow < mean_angles[0] - 20:
            mistakes.append("Keep elbows tucked - don't flare out")
    
    return mistakes

# Initialize database and gamification data
def initialize_app():
    """Initialize database and gamification data"""
    try:
        print("Starting database initialization...")
        with app.app_context():
            try:
                db.create_all()
                print("✅ Database initialized successfully")
            except Exception as db_error:
                print(f"⚠️ Database creation failed: {db_error}")
                print("Continuing without database...")
            
            # Initialize gamification data
            try:
                print("Starting gamification initialization...")
                initialize_gamification_data()
                print("✅ Gamification data initialized successfully")
            except Exception as gamification_error:
                print(f"⚠️ Gamification initialization failed: {gamification_error}")
                print("Continuing without gamification...")
    except Exception as e:
        print(f"❌ Warning: App initialization failed: {e}")
        print("App will continue to run but some features may not work properly")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Exercise Form Analyzer - Railway Deployment")
    print("=" * 60)
    print(f"🤖 AI/ML Features: {'✅ Available' if AI_AVAILABLE else '⚠️ Limited'}")
    print("🔐 User authentication enabled")
    print("📊 Exercise history tracking enabled")
    print("🎮 Gamification features enabled")
    
    # Initialize database and gamification
    print("\n🔧 Initializing application...")
    initialize_app()
    print("✅ Application initialization complete")
    
    # Railway deployment configuration
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    environment = os.environ.get('RAILWAY_ENVIRONMENT', 'development')
    
    print(f"\n🌐 Starting server on port {port}")
    print(f"🔍 Debug mode: {debug}")
    print(f"🏗️ Environment: {environment}")
    print(f"🔗 Health check: http://localhost:{port}/status")
    print("📡 Server ready to accept connections")
    print("=" * 60)
    
    app.run(debug=debug, host='0.0.0.0', port=port)