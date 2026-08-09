from celery_worker import celery_app
from models.schema import db, User, Application, PlacementDrive
from datetime import datetime, timedelta
import csv
import os

@celery_app.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    # Find drives ending in exactly 2 days
    upcoming_drives = PlacementDrive.query.filter(
        PlacementDrive.deadline > datetime.utcnow(),
        PlacementDrive.deadline < datetime.utcnow() + timedelta(days=2),
        PlacementDrive.status == 'approved'
    ).all()
    
    # Mocking Google Chat / Email Webhook
    for drive in upcoming_drives:
        message = f"Reminder: The deadline for {drive.job_title} at {drive.company.company_name} is approaching on {drive.deadline.strftime('%Y-%m-%d')}!"
        print(f"[WEBHOOK SIMULATION] Sent to all eligible students: {message}")
        
    return f"Daily Reminders Sent for {len(upcoming_drives)} drives"

@celery_app.task(name='tasks.generate_monthly_report')
def generate_monthly_report():
    # Admin monthly report logic
    drives_conducted = PlacementDrive.query.filter_by(status='closed').count()
    total_applications = Application.query.count()
    selected_students = Application.query.filter_by(status='selected').count()
    
    report_content = f"""
    <html>
    <body>
        <h2>Monthly Placement Report</h2>
        <ul>
            <li>Drives Conducted: {drives_conducted}</li>
            <li>Total Applications: {total_applications}</li>
            <li>Selected Students: {selected_students}</li>
        </ul>
    </body>
    </html>
    """
    
    # Mocking Email Send
    print(f"[EMAIL SIMULATION] Sending Monthly Report to Admin...\n{report_content}")
    
    # Optional: Write to a file to show it was generated
    with open('static/monthly_report.html', 'w') as f:
        f.write(report_content)
        
    return "Monthly Report Generated and Saved"

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
