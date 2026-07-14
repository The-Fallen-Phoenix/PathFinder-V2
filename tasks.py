from celery_worker import celery_app
from models import db, User, Application, PlacementDrive
from datetime import datetime, timedelta
import csv
import os

@celery_app.task
def send_daily_reminders():
    # Example logic to find drives ending soon and send reminders to eligible students
    upcoming_drives = PlacementDrive.query.filter(
        PlacementDrive.deadline > datetime.utcnow(),
        PlacementDrive.deadline < datetime.utcnow() + timedelta(days=2),
        PlacementDrive.status == 'approved'
    ).all()
    
    # In a real app, this would use a mailer or GChat webhook
    print(f"Daily Reminder Task: Found {len(upcoming_drives)} upcoming drives.")
    return "Daily Reminders Sent"

@celery_app.task
def generate_monthly_report():
    # Example logic for admin monthly report
    drives_conducted = PlacementDrive.query.filter_by(status='closed').count()
    total_applications = Application.query.count()
    selected_students = Application.query.filter_by(status='selected').count()
    
    report_content = f"""
    Monthly Placement Report:
    - Drives Conducted: {drives_conducted}
    - Total Applications: {total_applications}
    - Selected Students: {selected_students}
    """
    
    # Normally this would generate HTML/PDF and email to admin
    print("Monthly Report Task:", report_content)
    return "Monthly Report Generated"

@celery_app.task
def export_applications_csv(student_id):
    student = User.query.get(student_id)
    if not student or student.role != 'student':
        return "Invalid student"
        
    apps = Application.query.filter_by(student_id=student.student_profile.id).all()
    
    filename = f"applications_export_{student_id}.csv"
    filepath = os.path.join('static', filename)
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for app in apps:
            writer.writerow({
                'Student ID': student.student_profile.roll_no,
                'Company Name': app.drive.company.company_name,
                'Drive Title': app.drive.job_title,
                'Application Status': app.status,
                'Date': app.applied_on.strftime('%Y-%m-%d %H:%M:%S')
            })
            
    print(f"Export CSV Task: File {filename} created.")
    return filepath
