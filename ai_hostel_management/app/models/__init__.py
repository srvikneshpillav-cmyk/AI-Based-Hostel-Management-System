from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')  # 'admin' or 'student'
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    """Student profile model"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('users.username'), unique=True)
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    department = db.Column(db.String(100))
    year = db.Column(db.Integer)
    room_number = db.Column(db.String(20))
    parent_contact = db.Column(db.String(15))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='student')
    
    def __repr__(self):
        return f'<Student {self.full_name}>'

class Complaint(db.Model):
    """Complaint model"""
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('users.username'))
    title = db.Column(db.String(200), nullable=False)
    complaint = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # 'maintenance', 'food', 'roommate', etc
    status = db.Column(db.String(20), default='Pending')  # Pending, In Review, Resolved
    priority = db.Column(db.String(20), default='Normal')  # Low, Normal, High
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='complaints')
    
    def __repr__(self):
        return f'<Complaint {self.id}>'

class LeaveRequest(db.Model):
    """Leave request model"""
    __tablename__ = 'leave_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('users.username'))
    reason = db.Column(db.Text, nullable=False)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    responded_on = db.Column(db.DateTime)
    responded_by = db.Column(db.String(80))
    remarks = db.Column(db.Text)
    
    user = db.relationship('User', backref='leave_requests')
    
    def __repr__(self):
        return f'<LeaveRequest {self.id}>'

class Notice(db.Model):
    """Notice model"""
    __tablename__ = 'notices'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    image = db.Column(db.String(255))
    priority = db.Column(db.String(20), default='NORMAL')  # LOW, NORMAL, HIGH
    created_by = db.Column(db.String(80), db.ForeignKey('users.username'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    creator = db.relationship('User', backref='notices')
    
    def __repr__(self):
        return f'<Notice {self.title}>'

class Fee(db.Model):
    """Fee model"""
    __tablename__ = 'fees'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('users.username'), unique=True)
    semester = db.Column(db.String(20))
    amount = db.Column(db.Float)
    paid_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='Pending')  # Pending, Partial, Paid
    due_date = db.Column(db.Date)
    paid_date = db.Column(db.Date)
    transaction_id = db.Column(db.String(100))
    
    user = db.relationship('User', backref='fee')
    
    def __repr__(self):
        return f'<Fee {self.username}>'

class Room(db.Model):
    """Room model"""
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    floor = db.Column(db.Integer)
    capacity = db.Column(db.Integer)
    occupied = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='Available')  # Available, Occupied, Maintenance
    amenities = db.Column(db.Text)  # JSON format
    rent = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Room {self.room_number}>'

class FoodMenu(db.Model):
    """Food menu model"""
    __tablename__ = 'food_menu'
    
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20))
    breakfast = db.Column(db.String(200))
    lunch = db.Column(db.String(200))
    dinner = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FoodMenu {self.day}>'

class AuditLog(db.Model):
    """Audit log for tracking actions"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80))
    action = db.Column(db.String(200))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditLog {self.action}>'