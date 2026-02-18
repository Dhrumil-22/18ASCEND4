from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import User, Company, CareerPath, ProfileInfo, Experience, Roadmap, DiscussionThread, Question, Reply, MentorshipRequest, db

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/user/profile', methods=['GET'])
@login_required
def get_profile():
    profile = current_user.profile_info
    
    profile_data = {}
    if profile:
        profile_data = {
            'bio': profile.bio,
            'university': profile.university,
            'full_name': profile.full_name,
            'degree': profile.degree,
            'graduation_year': profile.graduation_year,
            'current_goal': profile.current_goal
        }
        
    skills = [s.name for s in current_user.skills]
    
    experiences = []
    for exp in current_user.experiences:
        experiences.append({
            'role': exp.role,
            'company': exp.company.name if exp.company else 'Unknown',
            'start_date': exp.start_date.isoformat() if exp.start_date else None,
            'end_date': exp.end_date.isoformat() if exp.end_date else None,
            'description': exp.description
        })

    return jsonify({
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role,
        'profile': profile_data,
        'skills': skills,
        'experiences': experiences
    })

@api.route('/user/profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()
    
    if not current_user.profile_info:
        profile = ProfileInfo(user_id=current_user.id)
        db.session.add(profile)
    else:
        profile = current_user.profile_info
        
    profile.bio = data.get('bio', profile.bio)
    profile.university = data.get('university', profile.university)
    profile.full_name = data.get('full_name', profile.full_name)
    profile.degree = data.get('degree', profile.degree)
    profile.graduation_year = data.get('graduation_year', profile.graduation_year)
    profile.current_goal = data.get('current_goal', profile.current_goal)
    
    db.session.commit()
    
    # Handle Skills (simple replace)
    if 'skills' in data:
        # Clear existing skills
        from models import Skill
        Skill.query.filter_by(user_id=current_user.id).delete()
        
        # Add new skills
        skills_list = data['skills'].split(',') if isinstance(data['skills'], str) else data['skills']
        for skill_name in skills_list:
            if skill_name.strip():
                skill = Skill(name=skill_name.strip(), user_id=current_user.id)
                db.session.add(skill)
        
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'}), 200

@api.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard():
    # User Info
    user_name = current_user.profile_info.full_name if current_user.profile_info and current_user.profile_info.full_name else current_user.username
    
    # Stats
    question_count = current_user.questions.count()
    thread_count = current_user.threads.count()
    # Mocking 'Mentor Responses' and 'Roadmaps Saved' for now as models might not support tracking yet
    mentor_responses = 0 
    roadmaps_saved = 0
    
    # Recommended Mentors (Logic: Users with role 'alumni' or 'mentor')
    # In a real app, this would use matching algorithms based on skills/goals
    mentors = User.query.filter(User.role.in_(['alumni', 'mentor'])).limit(3).all()
    mentors_data = []
    for m in mentors:
        company_name = "Unknown"
        job_role = "Mentor"
        # Try to find current experience
        latest_exp = m.experiences.order_by(Experience.id.desc()).first()
        if latest_exp:
            company_name = latest_exp.company.name if latest_exp.company else "Unknown"
            job_role = latest_exp.role
            
        mentors_data.append({
            'id': m.id,
            'name': m.profile_info.full_name if m.profile_info and m.profile_info.full_name else m.username,
            'role': job_role,
            'company': company_name,
            'trust_score': 95 # Mock score
        })
        
    # Recent Activity (Mocking global activity for now)
    # Fetch lates questions from other users
    latest_questions = Question.query.order_by(Question.created_at.desc()).limit(3).all()
    activity_feed = []
    for q in latest_questions:
        author_name = q.author.profile_info.full_name if q.author.profile_info and q.author.profile_info.full_name else q.author.username
        activity_feed.append({
            'text': f"<strong>{author_name}</strong> asked: {q.title}",
            'time': q.created_at.strftime("%Y-%m-%d")
        })

    return jsonify({
        'user_name': user_name,
        'points': current_user.points,
        'stats': {
            'questions': question_count,
            'responses': mentor_responses,
            'roadmaps': roadmaps_saved
        },
        'current_goal': current_user.profile_info.current_goal if current_user.profile_info else "Set a goal!",
        'mentors': mentors_data,
        'activity': activity_feed
    })

@api.route('/mentors', methods=['GET'])
@login_required
def get_all_mentors():
    mentors = User.query.filter(User.role.in_(['alumni', 'mentor'])).all()
    mentors_data = []
    for m in mentors:
        company_name = "Unknown"
        job_role = "Mentor"
        # Try to find current experience
        latest_exp = m.experiences.order_by(Experience.id.desc()).first()
        if latest_exp:
            company_name = latest_exp.company.name if latest_exp.company else "Unknown"
            job_role = latest_exp.role
            
        mentors_data.append({
            'id': m.id,
            'name': m.profile_info.full_name if m.profile_info and m.profile_info.full_name else m.username,
            'role': job_role,
            'company': company_name,
            'bio': m.profile_info.bio if m.profile_info else "No bio available.",
            'initials': (m.profile_info.full_name if m.profile_info and m.profile_info.full_name else m.username)[:2].upper()
        })
    return jsonify(mentors_data)

@api.route('/student/mentors', methods=['GET'])
@login_required
def get_connected_mentors():
    # Fetch mentors with accepted mentorship requests
    accepted_requests = MentorshipRequest.query.filter_by(student_id=current_user.id, status='accepted').all()
    
    mentors_data = []
    for req in accepted_requests:
        m = req.mentor
        company_name = "Unknown"
        job_role = "Mentor"
        # Try to find current experience
        latest_exp = m.experiences.order_by(Experience.id.desc()).first()
        if latest_exp:
            company_name = latest_exp.company.name if latest_exp.company else "Unknown"
            job_role = latest_exp.role
            
        mentors_data.append({
            'id': m.id,
            'name': m.profile_info.full_name if m.profile_info and m.profile_info.full_name else m.username,
            'role': job_role,
            'company': company_name,
            'bio': m.profile_info.bio if m.profile_info else "No bio available.",
            'initials': (m.profile_info.full_name if m.profile_info and m.profile_info.full_name else m.username)[:2].upper()
        })
    return jsonify(mentors_data)

@api.route('/messages', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    
    if not recipient_id or not content:
        return jsonify({'error': 'Recipient and content are required'}), 400
        
    # In a real app, we would save this to a Message model.
    # For now, we simulate success.
    
    return jsonify({'message': 'Message sent successfully'}), 200

@api.route('/companies', methods=['GET'])
def get_companies():
    companies = Company.query.all()
    companies_data = []
    for c in companies:
        companies_data.append({
            'name': c.name,
            'description': c.description,
            'logo_url': c.logo_url
        })
    return jsonify(companies_data)

@api.route('/career/paths', methods=['GET'])
def get_career_paths():
    paths = CareerPath.query.all()
    return jsonify([{
        'title': p.title,
        'description': p.description
    } for p in paths])

@api.route('/career/roadmaps', methods=['GET'])
def get_roadmaps():
    roadmaps = Roadmap.query.all()
    result = []
    for r in roadmaps:
        creator_name = r.creator.profile_info.full_name if r.creator.profile_info and r.creator.profile_info.full_name else r.creator.username
        result.append({
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'creator': creator_name,
            'saves': 120 # Mock
        })
    return jsonify(result)

@api.route('/career/roadmaps/<int:roadmap_id>', methods=['GET'])
def get_roadmap_detail(roadmap_id):
    r = Roadmap.query.get_or_404(roadmap_id)
    creator_name = r.creator.profile_info.full_name if r.creator.profile_info and r.creator.profile_info.full_name else r.creator.username
    
    return jsonify({
        'id': r.id,
        'title': r.title,
        'description': r.description,
        'steps': r.steps, 
        'creator': creator_name,
        'creator_role': r.creator.role,
        'saves': 120 # Mock
    })

@api.route('/discussions', methods=['GET'])
def get_discussions():
    threads = DiscussionThread.query.order_by(DiscussionThread.created_at.desc()).all()
    result = []
    for t in threads:
        author = t.author
        author_name = author.profile_info.full_name if author.profile_info and author.profile_info.full_name else author.username
        role = author.role
        result.append({
            'id': t.id,
            'title': t.title,
            'category': t.category,
            'author': author_name,
            'author_role': role,
            'created_at': t.created_at.strftime("%Y-%m-%d"),
            'likes': 42 + t.id * 2, # Mock
            'replies': 5 + t.id # Mock
        })
    return jsonify(result)
@api.route('/questions', methods=['GET'])
@login_required
def get_questions():
    questions = Question.query.order_by(Question.is_urgent.desc(), Question.bounty.desc(), Question.created_at.desc()).all()
    output = []
    for q in questions:
        author = q.author
        replies = []
        for r in q.replies:
             replies.append({
                 'id': r.id,
                 'content': r.content,
                 'author_name': r.author.profile_info.full_name if r.author.profile_info and r.author.profile_info.full_name else r.author.username,
                 'author_role': r.author.role,
                 'created_at': r.created_at.strftime("%Y-%m-%d")
             })

        output.append({
            'id': q.id,
            'title': q.title,
            'content': q.content,
            'is_urgent': q.is_urgent,
            'bounty': q.bounty,
            'author_name': author.profile_info.full_name if author.profile_info and author.profile_info.full_name else author.username,
            'author_initials': author.username[:2].upper(),
            'created_at': q.created_at.strftime("%Y-%m-%d"),
            'replies': replies
        })
    return jsonify(output)

@api.route('/questions', methods=['POST'])
@login_required
def create_question():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    is_urgent = data.get('is_urgent', False)
    bounty = int(data.get('bounty', 0)) if is_urgent else 0
    
    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400
        
    # Points Logic
    if is_urgent:
        if current_user.points < bounty:
             return jsonify({'error': 'Insufficient points for this bounty'}), 400
        # Deduct points
        current_user.points -= bounty
        
    question = Question(
        title=title,
        content=content,
        user_id=current_user.id,
        is_urgent=is_urgent,
        bounty=bounty
    )
    db.session.add(question)
    db.session.commit()
    
    return jsonify({'message': 'Question created successfully', 'id': question.id, 'points_remaining': current_user.points}), 201

@api.route('/questions/<int:question_id>/reply', methods=['POST'])
@login_required
def reply_question(question_id):
    if current_user.role not in ['mentor', 'alumni', 'admin']:
        return jsonify({'error': 'Unauthorized role'}), 403
    
    if current_user.role in ['mentor', 'alumni'] and not current_user.is_verified:
        return jsonify({'error': 'Account not verified by admin'}), 403

    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
        
    question = Question.query.get_or_404(question_id)
    
    reply = Reply(
        content=content,
        user_id=current_user.id,
        question_id=question.id
    )
    db.session.add(reply)
    db.session.commit()
    
    return jsonify({'message': 'Reply added successfully'}), 201

@api.route('/mentor/dashboard', methods=['GET'])
@login_required
def get_mentor_dashboard():
    # Only allow mentors/alumni
    if current_user.role not in ['mentor', 'alumni']:
        return jsonify({'error': 'Unauthorized'}), 403

    user_name = current_user.profile_info.full_name if current_user.profile_info and current_user.profile_info.full_name else current_user.username
    
    
    # Stats - Real Counts
    mentees_count = MentorshipRequest.query.filter_by(mentor_id=current_user.id, status='accepted').count()
    requests_count = MentorshipRequest.query.filter_by(mentor_id=current_user.id, status='pending').count()
    sessions_count = 0 # Placeholder as Session model doesn't exist yet
    
    # Fetch questions that have NO replies (unanswered) AND are NOT urgent
    # Using a left outer join to find questions with no replies
    unanswered_questions = Question.query.outerjoin(Reply).filter(Reply.id == None, Question.is_urgent != True).order_by(Question.created_at.desc()).limit(5).all()
    
    questions_data = []
    for q in unanswered_questions:
        author_name = q.author.profile_info.full_name if q.author.profile_info and q.author.profile_info.full_name else q.author.username
        questions_data.append({
            'id': q.id,
            'title': q.title,
            'content': q.content if q.content else "",
            'author': author_name if author_name else "Unknown",
            'author_initials': (author_name[:2].upper()) if author_name else "??",
            'time': q.created_at.strftime("%Y-%m-%d")
        })

    # Fetch Urgent Questions (Unanswered) sorted by bounty
    urgent_questions = Question.query.outerjoin(Reply).filter(Reply.id == None, Question.is_urgent == True).order_by(Question.bounty.desc(), Question.created_at.desc()).limit(5).all()
    
    urgent_data = []
    for q in urgent_questions:
        author_name = q.author.profile_info.full_name if q.author.profile_info and q.author.profile_info.full_name else q.author.username
        urgent_data.append({
            'id': q.id,
            'title': q.title,
            'content': q.content if q.content else "",
            'author': author_name if author_name else "Unknown",
            'author_initials': (author_name[:2].upper()) if author_name else "??",
            'time': q.created_at.strftime("%Y-%m-%d"),
            'bounty': q.bounty
        })

    # Total Unanswered Count (Urgent + General)
    total_unanswered_count = Question.query.outerjoin(Reply).filter(Reply.id == None).count()

    return jsonify({
        'user_name': user_name,
        'stats': {
            'mentees': mentees_count,
            'requests': requests_count,
            'sessions': sessions_count,
            'unanswered_questions': total_unanswered_count
        },
        'questions': questions_data,
        'urgent_questions': urgent_data
    })

@api.route('/mentor/questions', methods=['GET'])
@login_required
def get_all_mentor_questions():
    # Only allow mentors/alumni
    if current_user.role not in ['mentor', 'alumni']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Fetch ALL questions that have NO replies (unanswered)
    unanswered_questions = Question.query.outerjoin(Reply).filter(Reply.id == None).order_by(Question.created_at.desc()).all()
    
    questions_data = []
    for q in unanswered_questions:
        author_name = q.author.profile_info.full_name if q.author.profile_info and q.author.profile_info.full_name else q.author.username
        questions_data.append({
            'id': q.id,
            'title': q.title,
            'content': q.content,
            'author': author_name,
            'author_initials': author_name[:2].upper(),
            'time': q.created_at.strftime("%Y-%m-%d"),
            'is_urgent': q.is_urgent,
            'bounty': q.bounty
        })

    return jsonify(questions_data)

@api.route('/roadmaps', methods=['POST'])
@login_required
def create_roadmap():
    if current_user.role not in ['mentor', 'alumni', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    steps = data.get('steps') # Expecting JSON string or object
    
    if not title or not description:
        return jsonify({'error': 'Title and description are required'}), 400
        
    roadmap = Roadmap(
        title=title,
        description=description,
        steps=str(steps) if steps else None, # Store as string
        creator_id=current_user.id
    )
    db.session.add(roadmap)
    db.session.commit()
    
    return jsonify({'message': 'Roadmap created successfully', 'id': roadmap.id}), 201

@api.route('/admin/dashboard', methods=['GET'])
@login_required
def get_admin_dashboard():
    # Only allow admin
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    user_name = current_user.username
    
    # Stats
    total_users = User.query.count()
    total_mentors = User.query.filter(User.role.in_(['mentor', 'alumni'])).count()
    total_discussions = DiscussionThread.query.count()
    
    # Recent Registrations
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    users_data = []
    for u in recent_users:
        users_data.append({
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'joined': u.created_at.strftime("%Y-%m-%d") if hasattr(u, 'created_at') else 'N/A'
        })

    return jsonify({
        'user_name': user_name,
        'stats': {
            'users': total_users,
            'mentors': total_mentors,
            'discussions': total_discussions
        },
        'users': users_data
    })

@api.route('/mentor/mentees', methods=['GET'])
@login_required
def get_mentor_mentees():
    if current_user.role not in ['mentor', 'alumni']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    # Fetch accepted requests
    accepted_requests = MentorshipRequest.query.filter_by(mentor_id=current_user.id, status='accepted').all()
    
    mentees = []
    for req in accepted_requests:
        student = req.student
        name = student.profile_info.full_name if student.profile_info and student.profile_info.full_name else student.username
        mentees.append({
            'id': student.id,
            'name': name,
            'initials': name[:2].upper(),
            'goal': student.profile_info.current_goal if student.profile_info else 'No goal set'
        })
    return jsonify(mentees)

@api.route('/mentor/requests', methods=['GET'])
@login_required
def get_mentor_requests():
    if current_user.role not in ['mentor', 'alumni']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    pending_requests = MentorshipRequest.query.filter_by(mentor_id=current_user.id, status='pending').all()
    
    requests_data = []
    for req in pending_requests:
        student = req.student
        name = student.profile_info.full_name if student.profile_info and student.profile_info.full_name else student.username
        requests_data.append({
            'id': req.id,
            'name': name,
            'initials': name[:2].upper(),
            'date': req.created_at.strftime("%Y-%m-%d"),
            'message': req.message
        })
    return jsonify(requests_data)

@api.route('/mentorship/request', methods=['POST'])
@login_required
def create_mentorship_request():
    if current_user.role != 'student':
        return jsonify({'error': 'Only students can request mentorship'}), 403
        
    data = request.get_json()
    mentor_id = data.get('mentor_id')
    message = data.get('message')
    
    if not mentor_id or not message:
        return jsonify({'error': 'Mentor ID and message are required'}), 400
        
    # Check if request already exists
    existing = MentorshipRequest.query.filter_by(student_id=current_user.id, mentor_id=mentor_id, status='pending').first()
    if existing:
        return jsonify({'error': 'Request already pending'}), 400
        
    access_req = MentorshipRequest(
        student_id=current_user.id,
        mentor_id=mentor_id,
        message=message
    )
    db.session.add(access_req)
    db.session.commit()
    
    return jsonify({'message': 'Request sent successfully'}), 201

@api.route('/mentorship/request/<int:req_id>/respond', methods=['POST'])
@login_required
def respond_mentorship_request(req_id):
    if current_user.role not in ['mentor', 'alumni']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    req_obj = MentorshipRequest.query.get_or_404(req_id)
    
    if req_obj.mentor_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    action = data.get('action') # 'accept' or 'reject'
    
    if action == 'accept':
        req_obj.status = 'accepted'
    elif action == 'reject':
        req_obj.status = 'rejected'
    else:
        return jsonify({'error': 'Invalid action'}), 400
        
    db.session.commit()
    return jsonify({'message': f'Request {action}ed'})

@api.route('/admin/users', methods=['GET'])
@login_required
def get_admin_users():
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    
    users = User.query.order_by(User.id.desc()).all()
    users_data = []
    for u in users:
        users_data.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'is_verified': u.is_verified,
            'joined': u.created_at.strftime("%Y-%m-%d") if hasattr(u, 'created_at') else 'N/A'
        })
    return jsonify(users_data)

@api.route('/admin/verify_user/<int:user_id>', methods=['POST'])
@login_required
def verify_user(user_id):
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_verified = True
    db.session.commit()
    
    return jsonify({'message': f'User {user.username} verified successfully'})

@api.route('/admin/content', methods=['GET'])
@login_required
def get_admin_content():
    if current_user.role != 'admin': return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'companies_count': Company.query.count(),
        'paths_count': CareerPath.query.count(),
        'roadmaps_count': Roadmap.query.count()
    })
