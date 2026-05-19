import os
from app import create_app, db
from app.models import User, Student, Complaint, LeaveRequest, Notice, Room, FoodMenu, Fee

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Make objects available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Student': Student,
        'Complaint': Complaint,
        'LeaveRequest': LeaveRequest,
        'Notice': Notice,
        'Room': Room,
        'FoodMenu': FoodMenu,
        'Fee': Fee
    }

@app.cli.command()
def init_db():
    """Initialize database"""
    db.create_all()
    print('Database initialized!')

@app.cli.command()
def seed_db():
    """Seed database with sample data"""
    
    # Create admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@hostel.com',
            full_name='Admin User',
            role='admin',
            phone='9999999999'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created!')
    
    # Create sample student
    if not User.query.filter_by(username='student1').first():
        student_user = User(
            username='student1',
            email='student1@example.com',
            full_name='John Doe',
            role='student',
            phone='9876543210'
        )
        student_user.set_password('student123')
        db.session.add(student_user)
        db.session.commit()
        
        student = Student(
            username='student1',
            full_name='John Doe',
            department='Computer Science',
            year=2,
            phone='9876543210'
        )
        db.session.add(student)
        db.session.commit()
        print('Sample student created!')
    
    # Create sample rooms
    if not Room.query.first():
        rooms = [
            Room(room_number='101', floor=1, capacity=2, rent=5000),
            Room(room_number='102', floor=1, capacity=2, rent=5000),
            Room(room_number='201', floor=2, capacity=3, rent=7500),
            Room(room_number='202', floor=2, capacity=3, rent=7500),
        ]
        db.session.add_all(rooms)
        db.session.commit()
        print('Sample rooms created!')
    
    # Create food menu
    if not FoodMenu.query.first():
        menu = [
            FoodMenu(day='Monday', breakfast='Oats & Milk', lunch='Rice & Dal', dinner='Roti & Curry'),
            FoodMenu(day='Tuesday', breakfast='Bread & Butter', lunch='Chicken Rice', dinner='Pasta'),
            FoodMenu(day='Wednesday', breakfast='Cereals', lunch='Veg Biryani', dinner='Roti & Sabzi'),
        ]
        db.session.add_all(menu)
        db.session.commit()
        print('Food menu created!')

@app.cli.command()
def drop_db():
    """Drop all database tables"""
    db.drop_all()
    print('Database dropped!')

if __name__ == '__main__':
    # When running via `python run.py` on Windows the debug reloader sometimes
    # tries to use `socket.fromfd`, which isn't supported and results in
    # WinError 10038.  Disabling the reloader avoids the error.
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)