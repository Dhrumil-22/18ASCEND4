from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

# ==========================================
# User Module
# ==========================================

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student') # 'student', 'alumni', 'admin'
    is_verified = db.Column(db.Boolean, default=False) # For mentors
    points = db.Column(db.Integer, default=100) # Gamification points
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    skills = db.relationship('Skill', backref='user', lazy='dynamic')
    questions = db.relationship('Question', backref='author', lazy='dynamic')
    replies = db.relationship('Reply', backref='author', lazy='dynamic') # Added relationship
    threads = db.relationship('DiscussionThread', backref='author', lazy='dynamic')
    profile_info = db.relationship('ProfileInfo', backref='user', uselist=False)
    experiences = db.relationship('Experience', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=3600*24):
        from flask import current_app
        import jwt
        import time
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expiration},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_auth_token(token):
        from flask import current_app
        import jwt
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return f'<User {self.username}>'

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_urgent = db.Column(db.Boolean, default=False)
    bounty = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    replies = db.relationship('Reply', backref='question', lazy='dynamic')

class Reply(db.Model):
    __tablename__ = 'replies'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DiscussionThread(db.Model):
    __tablename__ = 'discussion_threads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProfileInfo(db.Model):
    __tablename__ = 'profile_info'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    bio = db.Column(db.Text)
    university = db.Column(db.String(128))
    full_name = db.Column(db.String(128))
    degree = db.Column(db.String(128))
    graduation_year = db.Column(db.Integer)
    current_goal = db.Column(db.String(256))
    company = db.Column(db.String(128)) # New field for Mentors
    job_title = db.Column(db.String(128)) # New field for Mentors


# ==========================================
# Career Exploration Module
# ==========================================

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True, nullable=False)
    logo_url = db.Column(db.String(256))
    description = db.Column(db.Text)
    
    # Relationships
    experiences = db.relationship('Experience', backref='company', lazy='dynamic')

class CareerPath(db.Model):
    __tablename__ = 'career_paths'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    roadmaps = db.relationship('Roadmap', backref='career_path', lazy='dynamic')

class Roadmap(db.Model):
    __tablename__ = 'roadmaps'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    steps = db.Column(db.Text) # Storing as JSON string or delineated text for simplicity
    career_path_id = db.Column(db.Integer, db.ForeignKey('career_paths.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', backref='roadmaps')

class Experience(db.Model):
    __tablename__ = 'experiences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    role = db.Column(db.String(128), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)

class MentorshipRequest(db.Model):
    __tablename__ = 'mentorship_requests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='pending') # pending, accepted, rejected
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], backref='mentorship_requests_sent')
    mentor = db.relationship('User', foreign_keys=[mentor_id], backref='mentorship_requests_received')
