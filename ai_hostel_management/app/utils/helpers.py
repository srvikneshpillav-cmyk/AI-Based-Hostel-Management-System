from flask import request
from functools import wraps
from app.models import AuditLog, db

def login_required_custom(f):
    """Custom login required decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session, redirect
        if 'username' not in session:
            return redirect('/login?next=' + request.url)
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session, redirect
        if 'role' not in session or session['role'] != 'admin':
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Require student role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session, redirect
        if 'role' not in session or session['role'] != 'student':
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def log_action(action, details=''):
    """Log user actions for audit trail"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import session
            result = f(*args, **kwargs)
            
            username = session.get('username', 'unknown')
            log = AuditLog(
                user=username,
                action=action,
                details=details,
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
            
            return result
        return decorated_function
    return decorator

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_pagination(page=1, per_page=10):
    """Get pagination parameters"""
    page = request.args.get('page', page, type=int)
    per_page = request.args.get('per_page', per_page, type=int)
    return page, per_page

def format_datetime(dt, format='%d %b %Y, %H:%M'):
    """Format datetime for display"""
    if dt:
        return dt.strftime(format)
    return ''