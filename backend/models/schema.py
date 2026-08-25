from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'company', 'student'
    status = db.Column(db.String(20), default='pending') # 'pending', 'approved', 'rejected', 'blacklisted'
    email = db.Column(db.String(255), unique=True, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CompanyProfile(db.Model):
    __tablename__ = 'company_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    hr_contact = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(200))
    
    user = db.relationship('User', backref=db.backref('company_profile', uselist=False, cascade="all, delete-orphan"))
    drives = db.relationship('PlacementDrive', backref='company', lazy=True, cascade="all, delete-orphan")

class StudentProfile(db.Model):
    __tablename__ = 'student_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    resume_link = db.Column(db.String(200))

    user = db.relationship('User', backref=db.backref('student_profile', uselist=False, cascade="all, delete-orphan"))
    applications = db.relationship('Application', backref='student', lazy=True, cascade="all, delete-orphan")

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drive'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profile.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    min_cgpa = db.Column(db.Float, default=0.0)
    eligible_branches = db.Column(db.String(200))
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending') # 'pending', 'approved', 'rejected'
    
    applications = db.relationship('Application', backref='drive', lazy=True, cascade="all, delete-orphan")

class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='applied') # 'applied', 'shortlisted', 'selected', 'rejected'
