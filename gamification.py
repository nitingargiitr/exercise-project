from models import db, UserLevel, Achievement, UserAchievement, Card, UserCard, DailyChallenge, UserDailyChallenge, ExerciseHistory
from datetime import datetime, date, timedelta
import random
import json

class GamificationManager:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
    
    def get_or_create_user_level(self, user_id):
        """Get or create user level record"""
        user_level = UserLevel.query.filter_by(user_id=user_id).first()
        if not user_level:
            user_level = UserLevel(user_id=user_id)
            db.session.add(user_level)
            db.session.commit()
        return user_level
    
    def calculate_workout_rewards(self, user_id, exercise_type, accuracy, mistakes=None):
        """Calculate XP and rewards for a workout"""
        user_level = self.get_or_create_user_level(user_id)
        
        # Base XP calculation
        base_xp = 10
        accuracy_bonus = int(accuracy * 0.5)  # Up to 50 bonus XP for perfect form
        perfect_bonus = 25 if accuracy >= 95 else 0
        
        total_xp = base_xp + accuracy_bonus + perfect_bonus
        
        # Update user stats
        user_level.experience_points += total_xp
        user_level.total_workouts += 1
        
        if accuracy >= 95:
            user_level.perfect_workouts += 1
        
        # Check for level up
        level_up = self.check_level_up(user_level)
        
        # Check for achievements
        new_achievements = self.check_achievements(user_id, user_level)
        
        # Award cards based on performance
        new_cards = self.award_cards(user_id, accuracy, exercise_type)
        
        # Update streak
        self.update_streak(user_level)
        
        db.session.commit()
        
        return {
            'xp_gained': total_xp,
            'level_up': level_up,
            'new_achievements': new_achievements,
            'new_cards': new_cards,
            'current_level': user_level.level,
            'current_xp': user_level.experience_points,
            'next_level_xp': user_level.get_next_level_xp()
        }
    
    def check_level_up(self, user_level):
        """Check if user should level up"""
        required_xp = user_level.get_next_level_xp()
        if user_level.experience_points >= required_xp:
            old_level = user_level.level
            user_level.level += 1
            # Don't subtract XP - let it accumulate for next level
            return {
                'leveled_up': True,
                'old_level': old_level,
                'new_level': user_level.level,
                'level_name': user_level.get_level_name()
            }
        return {'leveled_up': False}
    
    def check_achievements(self, user_id, user_level):
        """Check and award new achievements"""
        new_achievements = []
        
        # Get all possible achievements
        achievements = Achievement.query.filter_by(is_active=True).all()
        
        for achievement in achievements:
            # Check if user already has this achievement
            if UserAchievement.query.filter_by(user_id=user_id, achievement_id=achievement.id).first():
                continue
            
            # Check achievement requirements
            if self.check_achievement_requirement(user_id, achievement, user_level):
                # Award achievement
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
                db.session.add(user_achievement)
                
                # Award XP
                user_level.experience_points += achievement.xp_reward
                
                new_achievements.append({
                    'name': achievement.name,
                    'description': achievement.description,
                    'icon': achievement.icon,
                    'xp_reward': achievement.xp_reward
                })
        
        return new_achievements
    
    def check_achievement_requirement(self, user_id, achievement, user_level):
        """Check if user meets achievement requirement"""
        if achievement.category == 'streak':
            return user_level.streak_days >= achievement.requirement
        elif achievement.category == 'volume':
            return user_level.total_workouts >= achievement.requirement
        elif achievement.category == 'accuracy':
            if user_level.total_workouts > 0:
                avg_accuracy = self.get_average_accuracy(user_id)
                return avg_accuracy >= achievement.requirement
        elif achievement.category == 'perfect':
            return user_level.perfect_workouts >= achievement.requirement
        elif achievement.category == 'level':
            return user_level.level >= achievement.requirement
        
        return False
    
    def get_average_accuracy(self, user_id):
        """Calculate user's average accuracy"""
        histories = ExerciseHistory.query.filter_by(user_id=user_id).all()
        if not histories:
            return 0
        return sum(h.accuracy for h in histories) / len(histories)
    
    def award_cards(self, user_id, accuracy, exercise_type):
        """Award cards based on performance"""
        new_cards = []
        
        # Determine card rarity based on accuracy
        if accuracy >= 95:
            rarity_chance = {'legendary': 0.1, 'epic': 0.3, 'rare': 0.6}
        elif accuracy >= 85:
            rarity_chance = {'epic': 0.1, 'rare': 0.4, 'common': 0.5}
        elif accuracy >= 70:
            rarity_chance = {'rare': 0.2, 'common': 0.8}
        else:
            rarity_chance = {'common': 1.0}
        
        # Award 1-3 cards
        num_cards = random.randint(1, 3)
        
        for _ in range(num_cards):
            # Select rarity
            rand = random.random()
            cumulative = 0
            selected_rarity = 'common'
            
            for rarity, chance in rarity_chance.items():
                cumulative += chance
                if rand <= cumulative:
                    selected_rarity = rarity
                    break
            
            # Get random card of selected rarity
            cards = Card.query.filter_by(rarity=selected_rarity, is_active=True).all()
            if cards:
                card = random.choice(cards)
                
                # Check if user already has this card
                user_card = UserCard.query.filter_by(user_id=user_id, card_id=card.id).first()
                if user_card:
                    user_card.quantity += 1
                else:
                    user_card = UserCard(user_id=user_id, card_id=card.id)
                    db.session.add(user_card)
                
                new_cards.append({
                    'name': card.name,
                    'description': card.description,
                    'rarity': card.rarity,
                    'category': card.category,
                    'image_url': card.image_url
                })
        
        return new_cards
    
    def update_streak(self, user_level):
        """Update user's workout streak"""
        today = date.today()
        
        if user_level.last_workout_date:
            last_workout = user_level.last_workout_date.date()
            if last_workout == today:
                # Already worked out today, no change
                return
            elif last_workout == today - timedelta(days=1):
                # Consecutive day, increment streak
                user_level.streak_days += 1
            else:
                # Streak broken, reset to 1
                user_level.streak_days = 1
        else:
            # First workout
            user_level.streak_days = 1
        
        user_level.last_workout_date = datetime.utcnow()
    
    def get_user_stats(self, user_id):
        """Get comprehensive user statistics"""
        user_level = self.get_or_create_user_level(user_id)
        
        # Get recent workouts
        recent_workouts = ExerciseHistory.query.filter_by(user_id=user_id)\
            .order_by(ExerciseHistory.created_at.desc()).limit(10).all()
        
        # Get achievements
        achievements = db.session.query(Achievement, UserAchievement)\
            .join(UserAchievement, Achievement.id == UserAchievement.achievement_id)\
            .filter(UserAchievement.user_id == user_id)\
            .order_by(UserAchievement.earned_at.desc()).all()
        
        # Get cards
        cards = db.session.query(Card, UserCard)\
            .join(UserCard, Card.id == UserCard.card_id)\
            .filter(UserCard.user_id == user_id)\
            .order_by(UserCard.obtained_at.desc()).all()
        
        return {
            'level': user_level.level,
            'level_name': user_level.get_level_name(),
            'experience_points': user_level.experience_points,
            'next_level_xp': user_level.get_next_level_xp(),
            'total_workouts': user_level.total_workouts,
            'perfect_workouts': user_level.perfect_workouts,
            'streak_days': user_level.streak_days,
            'recent_workouts': [{
                'exercise_type': w.exercise_type,
                'accuracy': w.accuracy,
                'date': w.created_at.isoformat()
            } for w in recent_workouts],
            'achievements': [{
                'name': a.name,
                'description': a.description,
                'icon': a.icon,
                'earned_at': ua.earned_at.isoformat()
            } for a, ua in achievements],
            'cards': [{
                'name': c.name,
                'description': c.description,
                'rarity': c.rarity,
                'category': c.category,
                'quantity': uc.quantity,
                'obtained_at': uc.obtained_at.isoformat()
            } for c, uc in cards]
        }
    
    def create_daily_challenge(self, exercise_type, target_reps, target_accuracy, name=None):
        """Create a daily challenge"""
        if not name:
            name = f"Daily {exercise_type.title()} Challenge"
        
        challenge = DailyChallenge(
            name=name,
            description=f"Complete {target_reps} {exercise_type} with {target_accuracy}% accuracy",
            exercise_type=exercise_type,
            target_reps=target_reps,
            target_accuracy=target_accuracy,
            date=date.today()
        )
        
        db.session.add(challenge)
        db.session.commit()
        return challenge
    
    def complete_daily_challenge(self, user_id, challenge_id, score):
        """Mark daily challenge as completed"""
        user_challenge = UserDailyChallenge.query.filter_by(
            user_id=user_id, 
            challenge_id=challenge_id
        ).first()
        
        if not user_challenge:
            user_challenge = UserDailyChallenge(
                user_id=user_id,
                challenge_id=challenge_id
            )
            db.session.add(user_challenge)
        
        user_challenge.completed = True
        user_challenge.completed_at = datetime.utcnow()
        user_challenge.score = score
        
        # Award XP
        user_level = self.get_or_create_user_level(user_id)
        challenge = DailyChallenge.query.get(challenge_id)
        user_level.experience_points += challenge.xp_reward
        
        db.session.commit()
        return user_challenge

# Initialize default achievements and cards
def initialize_gamification_data():
    """Initialize default achievements and cards"""
    
    # Create default achievements
    achievements_data = [
        {
            'name': 'First Steps',
            'description': 'Complete your first workout',
            'icon': '🎯',
            'category': 'volume',
            'requirement': 1,
            'xp_reward': 25
        },
        {
            'name': 'Perfect Form',
            'description': 'Achieve 95% accuracy in a workout',
            'icon': '⭐',
            'category': 'accuracy',
            'requirement': 95,
            'xp_reward': 50
        },
        {
            'name': 'Streak Master',
            'description': 'Work out for 7 consecutive days',
            'icon': '🔥',
            'category': 'streak',
            'requirement': 7,
            'xp_reward': 100
        },
        {
            'name': 'Workout Warrior',
            'description': 'Complete 50 workouts',
            'icon': '💪',
            'category': 'volume',
            'requirement': 50,
            'xp_reward': 200
        },
        {
            'name': 'Perfectionist',
            'description': 'Achieve 10 perfect workouts',
            'icon': '🏆',
            'category': 'perfect',
            'requirement': 10,
            'xp_reward': 150
        }
    ]
    
    for ach_data in achievements_data:
        if not Achievement.query.filter_by(name=ach_data['name']).first():
            achievement = Achievement(**ach_data)
            db.session.add(achievement)
    
    # Create default cards
    cards_data = [
        {
            'name': 'Form Master',
            'description': 'Perfect your exercise form',
            'rarity': 'common',
            'category': 'form'
        },
        {
            'name': 'Strength Builder',
            'description': 'Build incredible strength',
            'rarity': 'rare',
            'category': 'strength'
        },
        {
            'name': 'Endurance King',
            'description': 'Unlimited stamina and endurance',
            'rarity': 'epic',
            'category': 'endurance'
        },
        {
            'name': 'Legendary Warrior',
            'description': 'The ultimate fitness champion',
            'rarity': 'legendary',
            'category': 'special'
        }
    ]
    
    for card_data in cards_data:
        if not Card.query.filter_by(name=card_data['name']).first():
            card = Card(**card_data)
            db.session.add(card)
    
    db.session.commit()

