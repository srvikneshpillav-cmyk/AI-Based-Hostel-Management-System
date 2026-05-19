from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models import db, Complaint, LeaveRequest, Notice, Fee, Room, FoodMenu, User
from app.forms import ComplaintForm, LeaveRequestForm
from app.utils.helpers import student_required
from app.utils.services import DashboardService, ComplaintService, LeaveService, NoticeService

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/')
@student_required
def dashboard():
    """Student dashboard"""
    username = session['username']
    user = User.query.filter_by(username=username).first()
    
    complaints_count = Complaint.query.filter_by(username=username).count()
    pending_leaves = LeaveRequest.query.filter_by(username=username, status='Pending').count()
    recent_notices = NoticeService.get_active_notices()[:5]
    fee = Fee.query.filter_by(username=username).first()
    
    return render_template('student/dashboard.html',
                         user=user,
                         complaints_count=complaints_count,
                         pending_leaves=pending_leaves,
                         recent_notices=recent_notices,
                         fee=fee)

@student_bp.route('/complaints')
@student_required
def complaints():
    """View my complaints"""
    username = session['username']
    complaints = ComplaintService.get_student_complaints(username)
    
    return render_template('student/complaints.html', complaints=complaints)

@student_bp.route('/complaint/create', methods=['GET', 'POST'])
@student_required
def create_complaint():
    """File a new complaint"""
    form = ComplaintForm()
    if form.validate_on_submit():
        ComplaintService.create_complaint(
            username=session['username'],
            title=form.title.data,
            complaint=form.complaint.data,
            category=form.category.data,
            priority=form.priority.data
        )
        flash('Complaint submitted successfully. We will review it soon.', 'success')
        return redirect(url_for('student.complaints'))
    
    return render_template('student/create_complaint.html', form=form)

@student_bp.route('/complaint/<int:complaint_id>')
@student_required
def complaint_detail(complaint_id):
    """View complaint details"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Verify ownership
    if complaint.username != session['username']:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('student.complaints'))
    
    return render_template('student/complaint_detail.html', complaint=complaint)

@student_bp.route('/complaint/<int:complaint_id>/delete', methods=['POST'])
@student_required
def delete_complaint(complaint_id):
    """Delete a complaint"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Verify ownership
    if complaint.username != session['username']:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('student.complaints'))
    
    # Only allow deletion if complaint is pending or in progress
    if complaint.status not in ['Pending', 'In Progress']:
        flash('You can only delete pending or in-progress complaints.', 'error')
        return redirect(url_for('student.complaints'))
    
    try:
        db.session.delete(complaint)
        db.session.commit()
        flash('Complaint deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete complaint. Please try again.', 'error')
    
    return redirect(url_for('student.complaints'))

@student_bp.route('/leaves')
@student_required
def leaves():
    """View my leave requests"""
    username = session['username']
    leaves = LeaveService.get_student_leaves(username)
    
    return render_template('student/leaves.html', leaves=leaves)

@student_bp.route('/leave/request', methods=['GET', 'POST'])
@student_required
def request_leave():
    """Request leave"""
    form = LeaveRequestForm()
    if form.validate_on_submit():
        LeaveService.request_leave(
            username=session['username'],
            reason=form.reason.data,
            from_date=form.from_date.data,
            to_date=form.to_date.data
        )
        flash('Leave request submitted successfully.', 'success')
        return redirect(url_for('student.leaves'))
    
    return render_template('student/request_leave.html', form=form)

@student_bp.route('/notices')
@student_required
def notices():
    """View notices"""
    notices = NoticeService.get_active_notices()
    return render_template('student/notices.html', notices=notices)

@student_bp.route('/fees')
@student_required
def fees():
    """View fee status"""
    username = session['username']
    fee = Fee.query.filter_by(username=username).first()
    
    return render_template('student/fees.html', fee=fee)

@student_bp.route('/rooms')
@student_required
def rooms():
    """View available rooms"""
    rooms = Room.query.filter_by(status='Available').all()
    return render_template('student/rooms.html', rooms=rooms)

@student_bp.route('/food-menu')
@student_required
def food_menu():
    """View food menu"""
    menu = FoodMenu.query.order_by(FoodMenu.created_at.desc()).all()
    return render_template('student/food_menu.html', menu=menu)

@student_bp.route('/profile')
@student_required
def profile():
    """Student profile"""
    user = User.query.filter_by(username=session['username']).first()
    return render_template('student/profile.html', user=user)

@student_bp.route('/api/my-stats')
@student_required
def api_my_stats():
    """API endpoint for student stats"""
    username = session['username']
    complaints = Complaint.query.filter_by(username=username).count()
    pending_leaves = LeaveRequest.query.filter_by(username=username, status='Pending').count()
    approved_leaves = LeaveRequest.query.filter_by(username=username, status='Approved').count()
    
    return jsonify({
        'complaints': complaints,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves
    })