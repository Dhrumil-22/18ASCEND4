from app import app, db
from models import User, Skill, Question, DiscussionThread, ProfileInfo, Company, CareerPath, Roadmap, Experience

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")
