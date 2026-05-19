from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models import db, Complaint, LeaveRequest, Notice, Student, User
from app.forms import ComplaintForm, LeaveRequestForm, NoticeForm
from app.utils.helpers import admin_required, student_required
from app.utils.services import DashboardService, ComplaintService, LeaveService, NoticeService
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard"""
    stats = DashboardService.get_admin_dashboard_stats()
    recent_complaints = DashboardService.get_recent_complaints(5)
    pending_leaves = DashboardService.get_pending_leaves(5)
    recent_notices = DashboardService.get_recent_notices(3)
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_complaints=recent_complaints,
                         pending_leaves=pending_leaves,
                         recent_notices=recent_notices)

@admin_bp.route('/students')
@admin_required
def students():
    """Student list with search"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        students = DashboardService.search_students(query)
    else:
        students = Student.query.paginate(page=page, per_page=15).items
    
    return render_template('admin/students.html',
                         students=students,
                         query=query)

@admin_bp.route('/student/<username>')
@admin_required
def student_detail(username):
    """Student detail view"""
    student = Student.query.filter_by(username=username).first_or_404()
    complaints = Complaint.query.filter_by(username=username).all()
    leaves = LeaveRequest.query.filter_by(username=username).all()
    
    return render_template('admin/student_detail.html',
                         student=student,
                         complaints=complaints,
                         leaves=leaves)

@admin_bp.route('/complaints')
@admin_required
def complaints():
    """View all complaints"""
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    category = request.args.get('category', '')
    
    q = Complaint.query
    
    if query:
        q = q.filter((Complaint.title.ilike(f'%{query}%')) |
                     (Complaint.complaint.ilike(f'%{query}%')))
    if status:
        q = q.filter_by(status=status)
    if category:
        q = q.filter_by(category=category)
    
    complaints = q.order_by(Complaint.created_at.desc()).all()
    
    stats = DashboardService.get_complaint_status_breakdown()
    by_category = DashboardService.get_complaint_by_category()
    
    return render_template('admin/complaints.html',
                         complaints=complaints,
                         stats=stats,
                         by_category=by_category,
                         query=query,
                         status=status,
                         category=category)

@admin_bp.route('/complaint/<int:complaint_id>', methods=['GET', 'POST'])
@admin_required
def complaint_detail(complaint_id):
    """View and respond to complaint"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if request.method == 'POST':
        status = request.form.get('status')
        response = request.form.get('response')
        
        complaint.status = status
        complaint.response = response
        complaint.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Complaint updated successfully.', 'success')
        return redirect(url_for('admin.complaints'))
    
    return render_template('admin/complaint_detail.html', complaint=complaint)

@admin_bp.route('/complaint/<int:complaint_id>/delete', methods=['POST'])
@admin_required
def delete_complaint(complaint_id):
    """Delete a complaint"""
    try:
        complaint = Complaint.query.get_or_404(complaint_id)
        db.session.delete(complaint)
        db.session.commit()
        flash('Complaint deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete complaint. Please try again.', 'error')
    
    return redirect(url_for('admin.complaints'))

@admin_bp.route('/leaves')
@admin_required
def leaves():
    """Manage leave requests"""
    status = request.args.get('status', '')
    
    q = LeaveRequest.query
    if status:
        q = q.filter_by(status=status)
    
    leaves = q.order_by(LeaveRequest.applied_on.desc()).all()
    
    return render_template('admin/leaves.html', leaves=leaves, status=status)

@admin_bp.route('/leave/<int:leave_id>/approve', methods=['POST'])
@admin_required
def approve_leave(leave_id):
    """Approve leave request"""
    remarks = request.form.get('remarks', '')
    LeaveService.approve_leave(leave_id, session['username'], remarks)
    flash('Leave approved.', 'success')
    return redirect(url_for('admin.leaves'))

@admin_bp.route('/leave/<int:leave_id>/reject', methods=['POST'])
@admin_required
def reject_leave(leave_id):
    """Reject leave request"""
    remarks = request.form.get('remarks', '')
    LeaveService.reject_leave(leave_id, session['username'], remarks)
    flash('Leave rejected.', 'info')
    return redirect(url_for('admin.leaves'))

@admin_bp.route('/notices')
@admin_required
def notices():
    """Manage notices"""
    notices = Notice.query.order_by(Notice.created_at.desc()).all()
    return render_template('admin/notices.html', notices=notices)

@admin_bp.route('/notice/create', methods=['GET', 'POST'])
@admin_required
def create_notice():
    """Create a new notice"""
    form = NoticeForm()
    if form.validate_on_submit():
        NoticeService.create_notice(
            title=form.title.data,
            description=form.description.data,
            created_by=session['username'],
            content=form.content.data,
            priority=form.priority.data
        )
        flash('Notice created successfully.', 'success')
        return redirect(url_for('admin.notices'))
    
    return render_template('admin/create_notice.html', form=form)

@admin_bp.route('/notice/<int:notice_id>/delete', methods=['POST'])
@admin_required
def delete_notice(notice_id):
    """Delete a notice"""
    NoticeService.delete_notice(notice_id)
    flash('Notice deleted.', 'success')
    return redirect(url_for('admin.notices'))

@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """API endpoint for dashboard stats (JSON)"""
    stats = DashboardService.get_admin_dashboard_stats()
    return jsonify(stats)

@admin_bp.route('/api/complaints/status')
@admin_required
def api_complaints_status():
    """API endpoint for complaint status breakdown"""
    data = DashboardService.get_complaint_status_breakdown()
    return jsonify(data)

@admin_bp.route('/api/search')
@admin_required
def api_search():
    """API endpoint for search"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'complaints')
    
    if search_type == 'students':
        results = DashboardService.search_students(query)
        data = [{'username': s.username, 'name': s.full_name, 'dept': s.department} for s in results]
    else:
        results = DashboardService.search_complaints(query)
        data = [{'id': c.id, 'title': c.title, 'status': c.status} for c in results]
    
    return jsonify(data)