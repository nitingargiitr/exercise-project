from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import os

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    name = db.Column(db.String(100), nullable=False)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # User preferences and settings
    preferred_exercises = db.Column(db.Text, nullable=True)  # JSON string of exercise preferences
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'email': self.email,
            'profile_picture': self.profile_picture,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
    
    def __repr__(self):
        return f'<UserSession {self.session_token}>'

class ExerciseHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_type = db.Column(db.String(50), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    mistakes = db.Column(db.Text, nullable=True)  # JSON string of mistakes
    video_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('exercise_history', lazy=True))
    
    def __repr__(self):
        return f'<ExerciseHistory {self.exercise_type} - {self.accuracy}%>'

# Gamification Models
class UserLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level = db.Column(db.Integer, default=1)
    experience_points = db.Column(db.Integer, default=0)
    total_workouts = db.Column(db.Integer, default=0)
    perfect_workouts = db.Column(db.Integer, default=0)
    streak_days = db.Column(db.Integer, default=0)
    last_workout_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('user_level', uselist=False))
    
    def __repr__(self):
        return f'<UserLevel {self.user_id} - Level {self.level}>'
    
    def get_level_name(self):
        if self.level <= 5:
            return "Newbie"
        elif self.level <= 15:
            return "Beginner"
        elif self.level <= 30:
            return "Intermediate"
        elif self.level <= 50:
            return "Advanced"
        elif self.level <= 75:
            return "Pro"
        else:
            return "Expert"
    
    def get_next_level_xp(self):
        return self.level * 100

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100), nullable=False)  # Icon class or emoji
    category = db.Column(db.String(50), nullable=False)  # 'streak', 'accuracy', 'volume', 'special'
    requirement = db.Column(db.Integer, nullable=False)  # Number required (e.g., 10 workouts, 90% accuracy)
    xp_reward = db.Column(db.Integer, default=50)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Achievement {self.name}>'

class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('user_achievements', lazy=True))
    achievement = db.relationship('Achievement', backref=db.backref('user_achievements', lazy=True))
    
    def __repr__(self):
        return f'<UserAchievement {self.user_id} - {self.achievement.name}>'

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rarity = db.Column(db.String(20), nullable=False)  # 'common', 'rare', 'epic', 'legendary'
    category = db.Column(db.String(50), nullable=False)  # 'form', 'strength', 'endurance', 'special'
    image_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Card {self.name} ({self.rarity})>'

class UserCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    obtained_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('user_cards', lazy=True))
    card = db.relationship('Card', backref=db.backref('user_cards', lazy=True))
    
    def __repr__(self):
        return f'<UserCard {self.user_id} - {self.card.name}>'

class DailyChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    exercise_type = db.Column(db.String(50), nullable=False)
    target_reps = db.Column(db.Integer, nullable=False)
    target_accuracy = db.Column(db.Float, nullable=False)
    xp_reward = db.Column(db.Integer, default=100)
    card_reward_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    card_reward = db.relationship('Card', backref=db.backref('daily_challenges', lazy=True))
    
    def __repr__(self):
        return f'<DailyChallenge {self.name}>'

class UserDailyChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('daily_challenge.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)
    
    user = db.relationship('User', backref=db.backref('user_daily_challenges', lazy=True))
    challenge = db.relationship('DailyChallenge', backref=db.backref('user_daily_challenges', lazy=True))
    
    def __repr__(self):
        return f'<UserDailyChallenge {self.user_id} - {self.challenge.name}>'
