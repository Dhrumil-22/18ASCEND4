from app import app, db
from models import User, ProfileInfo, Skill, Company, Experience, Question, DiscussionThread, Reply, CareerPath, Roadmap, MentorshipRequest
from datetime import date

def seed_data():
    with app.app_context():
        print("Dropping old database tables...")
        db.drop_all()
        print("Creating new database tables...")
        db.create_all()
        print("Checking database for missing data...")
        
        # Ensure at least one user exists
        student = User.query.filter_by(role='student').first()
        if not student:
            print("No student found. Creating demo student...")
            student = User(
                username="Demo Student",
                email="student@demo.com",
                role="student",
                is_verified=True # Students verified by default? Or irrelevant.
            )
            student.set_password("password123")
            db.session.add(student)
            db.session.commit()
        else:
            print(f"Using existing student: {student.username}")

        # Ensure Admin exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                username="Admin User",
                email="admin@ascend.com",
                role="admin",
                is_verified=True
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

        # Ensure Profile exists
        if not student.profile_info:
            print("Creating profile for student...")
            profile = ProfileInfo(
                user_id=student.id,
                bio="I am a demo student interested in AI and Web Development.",
                university="Demo University",
                full_name="Demo Student",
                degree="B.S. Computer Science",
                graduation_year=2026,
                current_goal="Become a Full Stack Developer"
            )
            db.session.add(profile)
            db.session.commit()

        # Create Skills
        skills = ["Python", "Flask", "JavaScript", "React"]
        for s_name in skills:
            if not Skill.query.filter_by(name=s_name, user_id=student.id).first():
                print(f"Adding skill: {s_name}")
                db.session.add(Skill(name=s_name, user_id=student.id))
        
        # Create Companies
        google = Company.query.filter_by(name="Google").first()
        if not google:
            print("Adding company: Google")
            google = Company(name="Google", description="Tech Giant", logo_url="https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg")
            db.session.add(google)
        
        microsoft = Company.query.filter_by(name="Microsoft").first()
        if not microsoft:
            print("Adding company: Microsoft")
            microsoft = Company(name="Microsoft", description="Software Corp", logo_url="https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg")
            db.session.add(microsoft)
            
        db.session.commit()

        # Create Experience
        if not Experience.query.filter_by(user_id=student.id).first():
            print("Adding experience...")
            exp = Experience(
                user_id=student.id,
                company_id=google.id,
                role="Software Engineering Intern",
                start_date=date(2024, 6, 1),
                end_date=date(2024, 9, 1),
                description="Worked on backend infrastructure."
            )
            db.session.add(exp)
        
        # Create Question
        q1 = Question.query.filter_by(user_id=student.id).first()
        if not q1:
            print("Adding question...")
            q1 = Question(
                title="How to optimize Flask SQLAlchemy queries?",
                content="I am facing N+1 problem. Any tips?",
                user_id=student.id
            )
            db.session.add(q1)
            db.session.commit()
            
        # Create Discussion Thread
        if not DiscussionThread.query.filter_by(user_id=student.id).first():
            print("Adding discussion thread...")
            t = DiscussionThread(
                title="The future of AI in Web Dev",
                category="Technology",
                user_id=student.id
            )
            db.session.add(t)

        # Create Mentors
        mentors_data = [
            {"username": "Dr. Sarah Chen", "email": "sarah@google.com", "role": "mentor", "company": "Google", "job": "Software Engineer Lead"},
            {"username": "Michael Torres", "email": "michael@stripe.com", "role": "mentor", "company": "Microsoft", "job": "Principal Engineer"},
            {"username": "Emily Watson", "email": "emily@netflix.com", "role": "mentor", "company": "Google", "job": "Data Scientist"}
        ]

        for m_data in mentors_data:
            mentor = User.query.filter_by(email=m_data["email"]).first()
            if not mentor:
                print(f"Creating mentor: {m_data['username']}")
                mentor = User(username=m_data["username"], email=m_data["email"], role=m_data["role"], is_verified=True)
                mentor.set_password("password123")
                db.session.add(mentor)
                db.session.commit()
                
                # Profile with new fields
                m_profile = ProfileInfo(
                    user_id=mentor.id,
                    full_name=m_data["username"],
                    current_goal=m_data["job"] + " at " + m_data["company"],
                    bio=f"Experienced {m_data['job']}.",
                    university="Tech University",
                    degree="PhD Computer Science",
                    graduation_year=2015,
                    company=m_data["company"],
                    job_title=m_data["job"]
                )
                db.session.add(m_profile)
                
                # Experience
                m_company = Company.query.filter_by(name=m_data["company"]).first()
                if m_company:
                    m_exp = Experience(
                        user_id=mentor.id,
                        company_id=m_company.id,
                        role=m_data["job"],
                        description="Leading teams."
                    )
                    db.session.add(m_exp)
                db.session.commit()

        # Create Reply from Mentor
        mentor = User.query.filter_by(email="sarah@google.com").first()
        if mentor and q1:
             if not Reply.query.filter_by(question_id=q1.id).first():
                 print("Adding reply...")
                 r1 = Reply(content="You should look into eager loading with joinedload options.", user_id=mentor.id, question_id=q1.id)
                 db.session.add(r1)
                 db.session.commit()

        # Create Career Paths
        paths = [
            {"title": "Software Engineering", "description": "Build software."},
            {"title": "Product Management", "description": "Manage products."},
            {"title": "Data Science", "description": "Analyze data."},
            {"title": "Investment Banking", "description": "Finance."}
        ]
        for p_data in paths:
            if not CareerPath.query.filter_by(title=p_data["title"]).first():
                print(f"Adding career path: {p_data['title']}")
                cp = CareerPath(title=p_data["title"], description=p_data["description"])
                db.session.add(cp)
        
        # Create Roadmaps
        roadmaps = [
            {"title": "Breaking into FAANG", "description": "Guide for new grads.", "user_email": "sarah@google.com"},
            {"title": "From Bootcamp to Senior", "description": "The journey.", "user_email": "michael@stripe.com"},
            {"title": "PM Interview Prep", "description": "Crack the PM interview.", "user_email": "emily@netflix.com"},
            {"title": "Data Science Progression", "description": "Junior to Lead.", "user_email": "emily@netflix.com"}
        ]
        for r_data in roadmaps:
            if not Roadmap.query.filter_by(title=r_data["title"]).first():
                creator = User.query.filter_by(email=r_data["user_email"]).first()
                if creator:
                    print(f"Adding roadmap: {r_data['title']}")
                    rm = Roadmap(title=r_data["title"], description=r_data["description"], creator_id=creator.id)
                    db.session.add(rm)

        # Create more Discussion Threads
        threads = [
            {"title": "Best resources for system design?", "category": "Interview Prep", "user_email": "student@demo.com"},
            {"title": "Transitioning to PM?", "category": "Career Change", "user_email": "sarah@google.com"},
            {"title": "Negotiating offered?", "category": "Compensation", "user_email": "michael@stripe.com"},
            {"title": "Masters for AI/ML?", "category": "Education", "user_email": "emily@netflix.com"}
        ]
        for t_data in threads:
             if not DiscussionThread.query.filter_by(title=t_data["title"]).first():
                 creator = User.query.filter_by(email=t_data["user_email"]).first()
                 if creator:
                     print(f"Adding thread: {t_data['title']}")
                     dt = DiscussionThread(title=t_data["title"], category=t_data["category"], user_id=creator.id)
                     db.session.add(dt)

        # Create Mentorship Requests
        # Student -> Sarah (Pending)
        sarah = User.query.filter_by(email="sarah@google.com").first()
        if sarah and student:
            if not MentorshipRequest.query.filter_by(student_id=student.id, mentor_id=sarah.id).first():
                print("Adding mentorship request...")
                req = MentorshipRequest(
                    student_id=student.id,
                    mentor_id=sarah.id,
                    status='pending',
                    message="I'd love to learn from your experience at Google!"
                )
                db.session.add(req)
        
        # Student -> Michael (Accepted)
        michael = User.query.filter_by(email="michael@stripe.com").first()
        if michael and student:
            if not MentorshipRequest.query.filter_by(student_id=student.id, mentor_id=michael.id).first():
                print("Adding accepted mentorship...")
                req2 = MentorshipRequest(
                    student_id=student.id,
                    mentor_id=michael.id,
                    status='accepted',
                    message="Can you mentor me on Backend systems?"
                )
                db.session.add(req2)

        db.session.commit()
        print("Database verification/seeding complete!")

if __name__ == "__main__":
    seed_data()
