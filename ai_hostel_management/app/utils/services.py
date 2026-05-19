from app.models import db, Complaint, LeaveRequest, Notice, Student, Fee, User
from sqlalchemy import func, desc

class DashboardService:
    """Service for dashboard statistics and data"""
    
    @staticmethod
    def get_admin_dashboard_stats():
        """Get key statistics for admin dashboard"""
        total_students = Student.query.count()
        total_complaints = Complaint.query.count()
        pending_complaints = Complaint.query.filter_by(status='Pending').count()
        resolved_complaints = Complaint.query.filter_by(status='Resolved').count()
        pending_leaves = LeaveRequest.query.filter_by(status='Pending').count()
        approved_leaves = LeaveRequest.query.filter_by(status='Approved').count()
        total_notices = Notice.query.count()
        
        return {
            'total_students': total_students,
            'total_complaints': total_complaints,
            'pending_complaints': pending_complaints,
            'resolved_complaints': resolved_complaints,
            'pending_leaves': pending_leaves,
            'approved_leaves': approved_leaves,
            'total_notices': total_notices,
            'resolution_rate': round((resolved_complaints / total_complaints * 100), 2) if total_complaints > 0 else 0
        }
    
    @staticmethod
    def get_complaint_status_breakdown():
        """Get complaint status distribution"""
        statuses = db.session.query(
            Complaint.status,
            func.count(Complaint.id).label('count')
        ).group_by(Complaint.status).all()
        
        return {status: count for status, count in statuses}
    
    @staticmethod
    def get_complaint_by_category():
        """Get complaint statistics by category"""
        categories = db.session.query(
            Complaint.category,
            func.count(Complaint.id).label('count')
        ).group_by(Complaint.category).all()
        
        return {cat: count for cat, count in categories}
    
    @staticmethod
    def get_recent_complaints(limit=10):
        """Get recent complaints"""
        return Complaint.query.order_by(desc(Complaint.created_at)).limit(limit).all()
    
    @staticmethod
    def get_pending_leaves(limit=10):
        """Get pending leave requests"""
        return LeaveRequest.query.filter_by(status='Pending').order_by(
            desc(LeaveRequest.applied_on)
        ).limit(limit).all()
    
    @staticmethod
    def get_recent_notices(limit=5):
        """Get recent notices"""
        return Notice.query.order_by(desc(Notice.created_at)).limit(limit).all()
    
    @staticmethod
    def search_complaints(query):
        """Search complaints by title or content"""
        return Complaint.query.filter(
            (Complaint.title.ilike(f'%{query}%')) |
            (Complaint.complaint.ilike(f'%{query}%'))
        ).all()
    
    @staticmethod
    def search_students(query):
        """Search students by name or username"""
        return Student.query.filter(
            (Student.full_name.ilike(f'%{query}%')) |
            (Student.username.ilike(f'%{query}%'))
        ).all()

class ComplaintService:
    """Service for complaint management"""
    
    @staticmethod
    def create_complaint(username, title, complaint, category, priority='Normal'):
        """Create a new complaint"""
        new_complaint = Complaint(
            username=username,
            title=title,
            complaint=complaint,
            category=category,
            priority=priority,
            status='Pending'
        )
        db.session.add(new_complaint)
        db.session.commit()
        return new_complaint
    
    @staticmethod
    def update_complaint_status(complaint_id, status, response=None):
        """Update complaint status"""
        complaint = Complaint.query.get(complaint_id)
        if complaint:
            complaint.status = status
            if response:
                complaint.response = response
            db.session.commit()
        return complaint
    
    @staticmethod
    def get_student_complaints(username):
        """Get complaints by a student"""
        return Complaint.query.filter_by(username=username).order_by(
            desc(Complaint.created_at)
        ).all()

class LeaveService:
    """Service for leave management"""
    
    @staticmethod
    def request_leave(username, reason, from_date, to_date):
        """Submit a leave request"""
        leave = LeaveRequest(
            username=username,
            reason=reason,
            from_date=from_date,
            to_date=to_date,
            status='Pending'
        )
        db.session.add(leave)
        db.session.commit()
        return leave
    
    @staticmethod
    def approve_leave(leave_id, admin_username, remarks=''):
        """Approve a leave request"""
        leave = LeaveRequest.query.get(leave_id)
        if leave:
            leave.status = 'Approved'
            leave.responded_by = admin_username
            leave.remarks = remarks
            from datetime import datetime
            leave.responded_on = datetime.utcnow()
            db.session.commit()
        return leave
    
    @staticmethod
    def reject_leave(leave_id, admin_username, remarks=''):
        """Reject a leave request"""
        leave = LeaveRequest.query.get(leave_id)
        if leave:
            leave.status = 'Rejected'
            leave.responded_by = admin_username
            leave.remarks = remarks
            from datetime import datetime
            leave.responded_on = datetime.utcnow()
            db.session.commit()
        return leave
    
    @staticmethod
    def get_student_leaves(username):
        """Get leaves for a student"""
        return LeaveRequest.query.filter_by(username=username).order_by(
            desc(LeaveRequest.applied_on)
        ).all()

class NoticeService:
    """Service for notice management"""
    
    @staticmethod
    def create_notice(title, description, created_by, content='', image=None, priority='NORMAL', expires_at=None):
        """Create a new notice"""
        notice = Notice(
            title=title,
            description=description,
            content=content,
            created_by=created_by,
            image=image,
            priority=priority,
            expires_at=expires_at
        )
        db.session.add(notice)
        db.session.commit()
        return notice
    
    @staticmethod
    def get_active_notices():
        """Get all active notices"""
        from datetime import datetime
        return Notice.query.filter(
            (Notice.expires_at.is_(None)) | (Notice.expires_at > datetime.utcnow())
        ).order_by(desc(Notice.created_at)).all()
    
    @staticmethod
    def delete_notice(notice_id):
        """Delete a notice"""
        notice = Notice.query.get(notice_id)
        if notice:
            db.session.delete(notice)
            db.session.commit()
        return True