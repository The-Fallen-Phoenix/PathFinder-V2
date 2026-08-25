import smtplib
from email.message import EmailMessage
from flask import current_app
from celery_worker import celery_app
from models.schema import db, User, Application, PlacementDrive, StudentProfile
from datetime import datetime, timedelta
import csv
import os

def send_email(recipient, subject, body):
    message = EmailMessage()
    message["From"] = current_app.config["MAIL_USERNAME"]
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(
        current_app.config["MAIL_SERVER"],
        current_app.config["MAIL_PORT"]
    ) as smtp:
        smtp.starttls()
        smtp.login(
            current_app.config["MAIL_USERNAME"],
            current_app.config["MAIL_PASSWORD"]
        )
        smtp.send_message(message)

@celery_app.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    upcoming_drives = PlacementDrive.query.filter(
        PlacementDrive.deadline > datetime.utcnow(),
        PlacementDrive.deadline < datetime.utcnow() + timedelta(days=2),
        PlacementDrive.status == 'approved'
    ).all()
    
    for drive in upcoming_drives:
        eligible_students = StudentProfile.query.filter(
            StudentProfile.cgpa >= drive.min_cgpa
        ).all()

        for student in eligible_students:
            if not student.user or not student.user.email:
                continue

            message = (
                f"Reminder: The deadline for {drive.job_title} at "
                f"{drive.company.company_name} is approaching on "
                f"{drive.deadline.strftime('%Y-%m-%d')}."
            )

            send_email(
                student.user.email,
                "Placement Drive Deadline Reminder",
                message
            )
        
    return f"Daily Reminders Sent for {len(upcoming_drives)} drives"

@celery_app.task(name='tasks.generate_monthly_report')
def generate_monthly_report():
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
    
    admin_email = current_app.config.get("ADMIN_EMAIL")
    if admin_email:
        send_email(
            admin_email,
            "Monthly Placement Report",
            report_content
        )
    
    filepath = os.path.join(current_app.static_folder, 'monthly_report.html')
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(report_content)
        
    return "Monthly Report Generated and Saved"

@celery_app.task
def export_applications_csv(student_id):
    student = User.query.get(student_id)
    if not student or student.role != 'student':
        return "Invalid student"
        
    apps = Application.query.filter_by(student_id=student.student_profile.id).all()
    
    filename = f"applications_export_{student_id}.csv"
    filepath = os.path.join(current_app.static_folder, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
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
            
    return filepath
