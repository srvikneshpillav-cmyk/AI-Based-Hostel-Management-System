from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    """Login form with validation"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('student', 'Student'), ('admin', 'Admin')], validators=[DataRequired()])

class RegisterForm(FlaskForm):
    """Registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class ComplaintForm(FlaskForm):
    """Complaint submission form"""
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    category = SelectField('Category', choices=[
        ('maintenance', 'Maintenance'),
        ('food', 'Food Quality'),
        ('roommate', 'Roommate Issue'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    complaint = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=2000)])
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('High', 'High')
    ], default='Normal')

class LeaveRequestForm(FlaskForm):
    """Leave request form"""
    reason = TextAreaField('Reason', validators=[DataRequired(), Length(min=10, max=500)])
    from_date = DateField('From Date', validators=[DataRequired()], format='%Y-%m-%d')
    to_date = DateField('To Date', validators=[DataRequired()], format='%Y-%m-%d')

class NoticeForm(FlaskForm):
    """Notice creation form"""
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    content = TextAreaField('Content', validators=[Length(max=5000)])
    priority = SelectField('Priority', choices=[
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High')
    ], default='NORMAL')
    image = FileField('Image')

class UpdateProfileForm(FlaskForm):
    """Update user profile"""
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[Length(max=500)])

class ChangePasswordForm(FlaskForm):
    """Change password form"""
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])