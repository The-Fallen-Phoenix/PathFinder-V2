from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.schema import db, User, CompanyProfile, StudentProfile, PlacementDrive, Application
from extensions import cache
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
        
        import json
        access_token = create_access_token(identity=json.dumps({'id': user.id, 'role': user.role}))
        return jsonify(access_token=access_token, role=user.role), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@api_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    new_user = User(
        username=data["username"],
        email=data.get("email"),
        role="student",
        status="approved"
    )
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

@api_bp.route('/admin/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    import json
    current_user = json.loads(get_jwt_identity())
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
    import json
    current_user = json.loads(get_jwt_identity())
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
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    data = request.get_json()
    company = CompanyProfile.query.get(company_id)
    if company:
        company.user.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Status updated'}), 200
    return jsonify({'message': 'Company not found'}), 404

@api_bp.route('/admin/students', methods=['GET'])
@jwt_required()
def get_students():
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    students = StudentProfile.query.all()
    res = [{
        'id': s.id,
        'full_name': s.full_name,
        'email': s.user.email if s.user else '',
        'roll_no': s.roll_no,
        'branch': s.branch,
        'cgpa': s.cgpa,
        'status': s.user.status if s.user else ''
    } for s in students]
    return jsonify(res), 200

@api_bp.route('/admin/students/<int:student_id>/status', methods=['PUT'])
@jwt_required()
def update_student_status(student_id):
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    data = request.get_json()
    student = StudentProfile.query.get(student_id)
    if student:
        student.user.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Student status updated'}), 200
    return jsonify({'message': 'Student not found'}), 404

@api_bp.route('/admin/drives', methods=['GET'])
@jwt_required()
def get_all_drives():
    import json
    current_user = json.loads(get_jwt_identity())
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
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    data = request.get_json()
    drive = PlacementDrive.query.get(drive_id)
    if drive:
        drive.status = data['status']
        db.session.commit()
        cache.clear()
        return jsonify({'message': 'Drive status updated'}), 200
    return jsonify({'message': 'Drive not found'}), 404

@api_bp.route('/admin/monthly_report', methods=['GET'])
@jwt_required()
def get_monthly_report():
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return "Unauthorized", 403
        
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_jobs = PlacementDrive.query.count()
    total_applications = Application.query.count()
    selected_students = Application.query.filter_by(status='selected').count()
    shortlisted_students = Application.query.filter_by(status='shortlisted').count()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Monthly Placement Activity Report</title>
        <style>
            body {{ font-family: Arial, Helvetica, sans-serif; padding: 20px; color: #000; background-color: #ffffff; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border: 2px solid #000; }}
            .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }}
            .title {{ font-size: 20px; font-weight: bold; color: #000; text-transform: uppercase; margin: 0; }}
            .date {{ font-size: 12px; color: #555; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .report-footer {{ margin-top: 30px; text-align: center; font-size: 11px; color: #555; border-top: 1px solid #000; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="title">Monthly Placement Activity Report</div>
                <div class="date">Generated on: {datetime.now().strftime('%B %d, %Y')}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Metric Description</th>
                        <th>Registered Count</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Total Registered Students</td>
                        <td><strong>{total_students}</strong></td>
                    </tr>
                    <tr>
                        <td>Total Partner Companies</td>
                        <td><strong>{total_companies}</strong></td>
                    </tr>
                    <tr>
                        <td>Total Placement Drives</td>
                        <td><strong>{total_jobs}</strong></td>
                    </tr>
                    <tr>
                        <td>Total Applications Received</td>
                        <td><strong>{total_applications}</strong></td>
                    </tr>
                    <tr>
                        <td>Total Students Selected</td>
                        <td><strong>{selected_students}</strong></td>
                    </tr>
                    <tr>
                        <td>Total Students Shortlisted</td>
                        <td><strong>{shortlisted_students}</strong></td>
                    </tr>
                </tbody>
            </table>
            
            <div class="report-footer">
                PathFinder Placement Portal - Activity Document
            </div>
        </div>
    </body>
    </html>
    """
    return html_content, 200

@api_bp.route('/company/drives', methods=['GET', 'POST'])
@jwt_required()
def company_drives():
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'company':
        return jsonify({'message': 'Unauthorized'}), 403
    
    company = CompanyProfile.query.filter_by(user_id=current_user['id']).first()
    
    if request.method == 'POST':
        if company.user.status != 'approved':
            return jsonify({'message': 'Cannot create drives unless your profile is approved by Admin.'}), 403

        data = request.get_json()
        deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
        new_drive = PlacementDrive(
            company_id=company.id,
            job_title=data['job_title'],
            job_description=data['job_description'],
            min_cgpa=float(data.get('min_cgpa', 0.0)),
            eligible_branches=data.get('eligible_branches', ''),
            deadline=deadline,
            status='pending'
        )
        db.session.add(new_drive)
        db.session.commit()
        return jsonify({'message': 'Drive created, pending approval'}), 201
    
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
    import json
    current_user = json.loads(get_jwt_identity())
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
        'applied_on': a.applied_on.strftime('%Y-%m-%d'),
        'resume_link': a.student.resume_link
    } for a in apps]
    return jsonify(res), 200

@api_bp.route('/company/applications/<int:app_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(app_id):
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'company':
        return jsonify({'message': 'Unauthorized'}), 403
        
    data = request.get_json()
    app = Application.query.get(app_id)
    if app:
        company = CompanyProfile.query.filter_by(user_id=current_user['id']).first()
        if app.drive.company_id == company.id:
            app.status = data['status']
            db.session.commit()
            return jsonify({'message': 'Application status updated'}), 200
    return jsonify({'message': 'Application not found'}), 404

@api_bp.route('/applications/<int:app_id>/offer_letter', methods=['GET'])
@jwt_required()
def generate_offer_letter(app_id):
    import json
    current_user = json.loads(get_jwt_identity())
    
    app = Application.query.get(app_id)
    if not app or app.status != 'selected':
        return "Application not selected or not found", 404
        
    if current_user['role'] == 'company':
        company = CompanyProfile.query.filter_by(user_id=current_user['id']).first()
        if not company or app.drive.company_id != company.id:
            return "Unauthorized", 403
    elif current_user['role'] == 'student':
        student = StudentProfile.query.filter_by(user_id=current_user['id']).first()
        if not student or app.student_id != student.id:
            return "Unauthorized", 403
    else:
        return "Unauthorized", 403

    company = CompanyProfile.query.get(app.drive.company_id)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Offer Letter - {app.student.full_name}</title>
        <style>
            body {{ font-family: 'Times New Roman', serif; padding: 50px; line-height: 1.6; color: #333; }}
            .header {{ text-align: center; border-bottom: 2px solid #0d4c94fb; padding-bottom: 20px; margin-bottom: 30px; }}
            .company-name {{ font-size: 28px; font-weight: bold; color: #0d4c94fb; }}
            .date {{ text-align: right; margin-bottom: 30px; }}
            .content {{ margin-bottom: 50px; }}
            .footer {{ border-top: 1px solid #ccc; padding-top: 20px; text-align: center; font-size: 14px; color: #777; }}
            .signature {{ margin-top: 50px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="company-name">{company.company_name}</div>
            <div>{company.website if company.website else 'Official Placement Offer'}</div>
        </div>
        
        <div class="date">Date: {datetime.now().strftime('%B %d, %Y')}</div>
        
        <div class="content">
            <p>Dear <strong>{app.student.full_name}</strong> (Roll No: {app.student.roll_no}),</p>
            
            <p>We are delighted to extend this formal offer of employment for the position of <strong>{app.drive.job_title}</strong> at {company.company_name}.</p>
            
            <p>Following your successful performance during our recent placement drive on the campus, we were very impressed by your skills, background, and attitude. We believe that your academic background in <strong>{app.student.branch}</strong> makes you a perfect fit for our team.</p>
            
            <p>Please review this offer letter and sign below to indicate your acceptance. We look forward to welcoming you aboard!</p>
        </div>
        
        <div class="signature">
            <p>Sincerely,</p>
            <p><strong>{company.hr_contact}</strong></p>
            <p>HR Department, {company.company_name}</p>
        </div>
        
        <div class="footer">
            Generated by PathFinder Placement Portal
        </div>
    </body>
    </html>
    """
    return html_content, 200

@api_bp.route('/student/profile', methods=['GET', 'PUT'])
@jwt_required()
def student_profile():
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'student':
        return jsonify({'message': 'Unauthorized'}), 403
        
    student = StudentProfile.query.filter_by(user_id=current_user['id']).first()
    
    if request.method == 'PUT':
        data = request.get_json()
        student.full_name = data.get('full_name', student.full_name)
        student.branch = data.get('branch', student.branch)
        student.cgpa = float(data.get('cgpa', student.cgpa))
        student.resume_link = data.get('resume_link', student.resume_link)
        if data.get('email') and student.user:
            student.user.email = data['email']
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200

    return jsonify({
        'full_name': student.full_name,
        'email': student.user.email if student.user else '',
        'roll_no': student.roll_no,
        'branch': student.branch,
        'cgpa': student.cgpa,
        'graduation_year': student.graduation_year,
        'resume_link': student.resume_link or ''
    }), 200

@api_bp.route('/drives', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
def get_drives():
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
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'student':
        return jsonify({'message': 'Unauthorized'}), 403
        
    student = StudentProfile.query.filter_by(user_id=current_user['id']).first()
    drive = PlacementDrive.query.filter_by(id=drive_id, status='approved').first()
    
    if not drive:
        return jsonify({'message': 'Drive not available'}), 404
        
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
    import json
    current_user = json.loads(get_jwt_identity())
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

@api_bp.route('/export/applications', methods=['POST'])
@jwt_required()
def trigger_export():
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'student':
        return jsonify({'message': 'Unauthorized'}), 403
        
    from tasks import export_applications_csv
    task = export_applications_csv.delay(current_user['id'])
    return jsonify({'message': 'Export started', 'task_id': task.id}), 202

@api_bp.route('/export/status/<task_id>', methods=['GET'])
@jwt_required()
def get_export_status(task_id):
    import json
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'student':
        return jsonify({'message': 'Unauthorized'}), 403
        
    from celery.result import AsyncResult
    from celery_worker import celery_app
    
    res = AsyncResult(task_id, app=celery_app)
    if res.ready():
        if res.failed():
            return jsonify({'status': 'FAILURE', 'error': str(res.result)}), 500
        filename = f"applications_export_{current_user['id']}.csv"
        download_url = f"/static/{filename}"
        return jsonify({'status': 'SUCCESS', 'download_url': download_url}), 200
        
    return jsonify({'status': 'PENDING'}), 200
