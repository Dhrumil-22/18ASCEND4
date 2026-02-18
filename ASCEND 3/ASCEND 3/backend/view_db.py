from app import app, db
from models import User, ProfileInfo

def view_data():
    with app.app_context():
        print("\n=== USERS ===")
        users = User.query.all()
        if not users:
            print("No users found.")
        for u in users:
            print(f"ID: {u.id} | Username: {u.username} | Email: {u.email} | Role: {u.role}")

        print("\n=== PROFILES ===")
        profiles = ProfileInfo.query.all()
        if not profiles:
            print("No profiles found.")
        for p in profiles:
            user = User.query.get(p.user_id)
            username = user.username if user else "Unknown"
            print(f"User: {username} | Uni: {p.university} | Bio: {p.bio[:30]}...")

        print("\n=== SKILLS ===")
        from models import Skill
        skills = Skill.query.all()
        for s in skills:
            print(f"User ID: {s.user_id} | Skill: {s.name}")

        print("\n=== EXPERIENCE ===")
        from models import Experience
        experiences = Experience.query.all()
        for e in experiences:
            print(f"User ID: {e.user_id} | Role: {e.role} | Company: {e.company.name if e.company else 'Unknown'}")

if __name__ == "__main__":
    view_data()
