from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, CompanyProfile, StudentProfile, PlacementDrive, Application
from app import cache
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        if user.status != 'approved':
            return jsonify({'message': f'Account is {user.status}'}), 403
        
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify(access_token=access_token, role=user.role), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@api_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    new_user = User(username=data['username'], role='student', status='approved')
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    student_profile = StudentProfile(
        user_id=new_user.id,
        full_name=data['full_name'],
        roll_no=data['roll_no'],
        branch=data['branch'],
        cgpa=float(data['cgpa']),
        graduation_year=int(data['graduation_year'])
    )
    db.session.add(student_profile)
    db.session.commit()

    return jsonify({'message': 'Student registered successfully'}), 201

@api_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    new_user = User(username=data['username'], role='company', status='pending')
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    company_profile = CompanyProfile(
        user_id=new_user.id,
        company_name=data['company_name'],
        hr_contact=data['hr_contact'],
        website=data.get('website', '')
    )
    db.session.add(company_profile)
    db.session.commit()

    return jsonify({'message': 'Company registered, pending admin approval'}), 201

# --- Admin APIs ---

@api_bp.route('/admin/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_jobs = PlacementDrive.query.count()
    total_applications = Application.query.count()
    
    return jsonify({
        'total_students': total_students,
        'total_companies': total_companies,
        'total_jobs': total_jobs,
        'total_applications': total_applications
    }), 200

@api_bp.route('/admin/companies', methods=['GET'])
@jwt_required()
def get_companies():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    companies = CompanyProfile.query.all()
    res = [{
        'id': c.id,
        'company_name': c.company_name,
        'status': c.user.status,
        'hr_contact': c.hr_contact,
        'website': c.website
    } for c in companies]
    return jsonify(res), 200

@api_bp.route('/admin/companies/<int:company_id>/status', methods=['PUT'])
@jwt_required()
def update_company_status(company_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    data = request.get_json()
    company = CompanyProfile.query.get(company_id)
    if company:
        company.user.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Status updated'}), 200
    return jsonify({'message': 'Company not found'}), 404

@api_bp.route('/admin/drives', methods=['GET'])
@jwt_required()
def get_all_drives():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    drives = PlacementDrive.query.all()
    res = [{
        'id': d.id,
        'company_name': d.company.company_name,
        'job_title': d.job_title,
        'status': d.status,
        'deadline': d.deadline.strftime('%Y-%m-%d')
    } for d in drives]
    return jsonify(res), 200

@api_bp.route('/admin/drives/<int:drive_id>/status', methods=['PUT'])
@jwt_required()
def update_drive_status(drive_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    data = request.get_json()
    drive = PlacementDrive.query.get(drive_id)
    if drive:
        drive.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Drive status updated'}), 200
    return jsonify({'message': 'Drive not found'}), 404


# --- Company APIs ---

@api_bp.route('/company/drives', methods=['GET', 'POST'])
@jwt_required()
def company_drives():
    current_user = get_jwt_identity()
    if current_user['role'] != 'company':
        return jsonify({'message': 'Unauthorized'}), 403
    
    company = CompanyProfile.query.filter_by(user_id=current_user['id']).first()
    
    if request.method == 'POST':
        data = request.get_json()
        deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
        new_drive = PlacementDrive(
            company_id=company.id,
            job_title=data['job_title'],
            job_description=data['job_description'],
            min_cgpa=float(data.get('min_cgpa', 0.0)),
            eligible_branches=data.get('eligible_branches', ''),
            deadline=deadline,
            status='pending' # Needs admin approval
        )
        db.session.add(new_drive)
        db.session.commit()
        return jsonify({'message': 'Drive created, pending approval'}), 201
    
    # GET drives for this company
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    res = [{
        'id': d.id,
        'job_title': d.job_title,
        'job_description': d.job_description,
        'min_cgpa': d.min_cgpa,
        'deadline': d.deadline.strftime('%Y-%m-%d'),
        'status': d.status
    } for d in drives]
    return jsonify(res), 200

@api_bp.route('/company/drives/<int:drive_id>/applications', methods=['GET'])
@jwt_required()
def company_drive_applications(drive_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'company':
        return jsonify({'message': 'Unauthorized'}), 403
    
    company = CompanyProfile.query.filter_by(user_id=current_user['id']).first()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return jsonify({'message': 'Drive not found'}), 404
        
    apps = Application.query.filter_by(drive_id=drive.id).all()
    res = [{
        'id': a.id,
        'student_id': a.student.id,
        'student_name': a.student.full_name,
        'roll_no': a.student.roll_no,
        'branch': a.student.branch,
        'cgpa': a.student.cgpa,
        'status': a.status,
        'applied_on': a.applied_on.strftime('%Y-%m-%d')
    } for a in apps]
    return jsonify(res), 200

@api_bp.route('/company/applications/<int:app_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(app_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'company':
        return jsonify({'message': 'Unauthorized'}), 403
        
    data = request.get_json()
    app = Application.query.get(app_id)
    if app:
        # Check if this company owns the drive
        company = CompanyProfile.query.filter_by(user_id=current_user['id']).first()
        if app.drive.company_id == company.id:
            app.status = data['status']
            db.session.commit()
            return jsonify({'message': 'Application status updated'}), 200
    return jsonify({'message': 'Application not found'}), 404


# --- Student APIs ---

@api_bp.route('/student/profile', methods=['GET'])
@jwt_required()
def student_profile():
    current_user = get_jwt_identity()
    if current_user['role'] != 'student':
        return jsonify({'message': 'Unauthorized'}), 403
        
    student = StudentProfile.query.filter_by(user_id=current_user['id']).first()
    return jsonify({
        'full_name': student.full_name,
        'roll_no': student.roll_no,
        'branch': student.branch,
        'cgpa': student.cgpa,
        'graduation_year': student.graduation_year
    }), 200

@api_bp.route('/drives', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
def get_drives():
    # Show approved drives
    drives = PlacementDrive.query.filter_by(status='approved').all()
    res = []
    for d in drives:
        res.append({
            'id': d.id,
            'company_name': d.company.company_name,
            'job_title': d.job_title,
            'job_description': d.job_description,
            'min_cgpa': d.min_cgpa,
            'deadline': d.deadline.strftime('%Y-%m-%d')
        })
    return jsonify(res), 200

@api_bp.route('/drives/<int:drive_id>/apply', methods=['POST'])
@jwt_required()
def apply_to_drive(drive_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'student':
        return jsonify({'message': 'Unauthorized'}), 403
        
    student = StudentProfile.query.filter_by(user_id=current_user['id']).first()
    drive = PlacementDrive.query.filter_by(id=drive_id, status='approved').first()
    
    if not drive:
        return jsonify({'message': 'Drive not available'}), 404
        
    # Check if already applied
    existing_app = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing_app:
        return jsonify({'message': 'Already applied'}), 400
        
    if student.cgpa < drive.min_cgpa:
        return jsonify({'message': 'CGPA criteria not met'}), 400
        
    new_app = Application(
        student_id=student.id,
        drive_id=drive.id,
        status='applied'
    )
    db.session.add(new_app)
    db.session.commit()
    return jsonify({'message': 'Applied successfully'}), 201

@api_bp.route('/student/applications', methods=['GET'])
@jwt_required()
def student_applications():
    current_user = get_jwt_identity()
    if current_user['role'] != 'student':
        return jsonify({'message': 'Unauthorized'}), 403
        
    student = StudentProfile.query.filter_by(user_id=current_user['id']).first()
    apps = Application.query.filter_by(student_id=student.id).all()
    
    res = [{
        'id': a.id,
        'company_name': a.drive.company.company_name,
        'job_title': a.drive.job_title,
        'status': a.status,
        'applied_on': a.applied_on.strftime('%Y-%m-%d')
    } for a in apps]
    return jsonify(res), 200

# --- Celery Trigger APIs ---

@api_bp.route('/export/applications', methods=['POST'])
@jwt_required()
def trigger_export():
    current_user = get_jwt_identity()
    if current_user['role'] != 'student':
        return jsonify({'message': 'Unauthorized'}), 403
        
    from tasks import export_applications_csv
    task = export_applications_csv.delay(current_user['id'])
    return jsonify({'message': 'Export started', 'task_id': task.id}), 202
