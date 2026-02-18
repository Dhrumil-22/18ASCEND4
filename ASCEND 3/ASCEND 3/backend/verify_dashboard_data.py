from app import app, db
from models import User, Question, Reply, MentorshipRequest

def verify_data():
    with app.app_context():
        print("VERIFICATION START")
        
        mentor = User.query.filter_by(role='mentor').first()
        if not mentor:
            print("NO MENTOR FOUND")
            return

        print(f"Mentor: {mentor.username}")

        # Unanswered Count
        unanswered_count = Question.query.outerjoin(Reply).filter(Reply.id == None).count()
        print(f"Total Unanswered: {unanswered_count}")
        
        # Urgent Count
        urgent_count = Question.query.outerjoin(Reply).filter(Reply.id == None, Question.is_urgent == True).count()
        print(f"Urgent Unanswered: {urgent_count}")

        # List first 3 urgent
        urgent_qs = Question.query.outerjoin(Reply).filter(Reply.id == None, Question.is_urgent == True).limit(3).all()
        for q in urgent_qs:
            print(f"  [URGENT] {q.id}: {q.title}")

        # List first 3 general (non-urgent)
        general_qs = Question.query.outerjoin(Reply).filter(Reply.id == None, Question.is_urgent != True).limit(3).all()
        for q in general_qs:
            print(f"  [GENERAL] {q.id}: {q.title}")

        print("VERIFICATION END")

if __name__ == "__main__":
    verify_data()
