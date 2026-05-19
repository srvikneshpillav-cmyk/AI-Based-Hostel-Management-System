from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models import db, User, Student, Complaint, LeaveRequest, Notice
from app.forms import LoginForm, RegisterForm
from app.utils.helpers import log_action
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

# root redirect to login to handle requests at '/'
@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data) and user.is_active:
            # Validate that the selected role matches user's assigned role
            if user.role != form.role.data:
                flash(f'Invalid role selection. You are registered as a {user.role}.', 'error')
                return redirect(url_for('auth.login'))
            
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = '/admin' if user.role == 'admin' else '/student'
            
            flash(f'Welcome, {user.full_name}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            role='student'
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Create student profile
        student = Student(username=user.username, full_name=user.full_name)
        db.session.add(student)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
def profile():
    """User profile view"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(username=session['username']).first()
    return render_template('profile.html', user=user)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password recovery"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # In production, send email with reset token
            flash('Password reset link sent to email.', 'info')
        else:
            flash('Email not found.', 'error')
        
        return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html')