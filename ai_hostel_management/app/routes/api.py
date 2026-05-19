from flask import Blueprint, render_template, jsonify
from app.models import db, Complaint, LeaveRequest, Notice, User, Student
from sqlalchemy import func

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """Get comprehensive dashboard statistics"""
    stats = {
        'total_students': Student.query.count(),
        'total_users': User.query.count(),
        'total_complaints': Complaint.query.count(),
        'complaint_pending': Complaint.query.filter_by(status='Pending').count(),
        'complaint_resolved': Complaint.query.filter_by(status='Resolved').count(),
        'total_leaves': LeaveRequest.query.count(),
        'leave_pending': LeaveRequest.query.filter_by(status='Pending').count(),
        'leave_approved': LeaveRequest.query.filter_by(status='Approved').count(),
        'total_notices': Notice.query.count()
    }
    return jsonify(stats)

@api_bp.route('/complaints/by-category', methods=['GET'])
def complaints_by_category():
    """Get complaints by category"""
    data = db.session.query(
        Complaint.category,
        func.count(Complaint.id).label('count')
    ).group_by(Complaint.category).all()
    
    result = {cat: count for cat, count in data}
    return jsonify(result)

@api_bp.route('/complaints/by-status', methods=['GET'])
def complaints_by_status():
    """Get complaints by status"""
    data = db.session.query(
        Complaint.status,
        func.count(Complaint.id).label('count')
    ).group_by(Complaint.status).all()
    
    result = {status: count for status, count in data}
    return jsonify(result)

@api_bp.route('/complaints/by-priority', methods=['GET'])
def complaints_by_priority():
    """Get complaints by priority"""
    data = db.session.query(
        Complaint.priority,
        func.count(Complaint.id).label('count')
    ).group_by(Complaint.priority).all()
    
    result = {priority: count for priority, count in data}
    return jsonify(result)

@api_bp.route('/leaves/by-status', methods=['GET'])
def leaves_by_status():
    """Get leaves by status"""
    data = db.session.query(
        LeaveRequest.status,
        func.count(LeaveRequest.id).label('count')
    ).group_by(LeaveRequest.status).all()
    
    result = {status: count for status, count in data}
    return jsonify(result)

@api_bp.route('/notices/recent/<int:limit>', methods=['GET'])
def recent_notices(limit=5):
    """Get recent notices"""
    notices = Notice.query.order_by(Notice.created_at.desc()).limit(limit).all()
    result = [{'id': n.id, 'title': n.title, 'priority': n.priority, 'created_at': n.created_at.isoformat()} 
              for n in notices]
    return jsonify(result)

@api_bp.route('/students/by-department', methods=['GET'])
def students_by_department():
    """Get students by department"""
    data = db.session.query(
        Student.department,
        func.count(Student.id).label('count')
    ).group_by(Student.department).all()
    
    result = {dept: count for dept, count in data}
    return jsonify(result)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'hostel-management-api'})