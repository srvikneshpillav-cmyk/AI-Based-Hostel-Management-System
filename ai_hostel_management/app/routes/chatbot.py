"""
Chatbot AI Assistant Module
Provides intelligent responses for student and admin queries
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import random

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api')

# Knowledge base for chatbot responses
CHATBOT_RESPONSES = {
    # Complaint related
    'complaint': [
        'You can file a complaint by going to the Complaints section. Click on "File New Complaint", select the category, and describe the issue.',
        'To view your complaint status, go to "My Complaints" section where you can see all your filed complaints and their current status.',
        'Complaints are typically reviewed within 24-48 hours by the admin team.',
    ],
    
    # Leave related
    'leave': [
        'To apply for leave, go to the "Leave Requests" section and fill in the dates and reason for your leave.',
        'Your leave request will be reviewed and approved/rejected by the admin. You can check the status in "Leave Status".',
        'You can apply for leave up to 14 days in advance.',
    ],
    
    # Notice related
    'notice': [
        'Notices are important announcements from the hostel administration. You can view all notices in the "Student Notices" section.',
        'Notices include information about hostel policies, events, maintenance schedules, and other important updates.',
        'You will be notified when new notices are posted.',
    ],
    
    # Fee related
    'fee': [
        'Your fee details and payment status can be viewed in the "Fees" section.',
        'If you have any dispute regarding fees, please contact the admin office or file a complaint.',
        'Fees are typically due on the first day of each month.',
    ],
    
    # Room related
    'room': [
        'Room assignments and details are available in the "Rooms" section.',
        'If you need to change your room or have issues with your room, please contact the admin or file a complaint.',
        'Room maintenance requests should be filed through the complaints section.',
    ],
    
    # General help
    'hello': [
        'Hello! Welcome to Hostel AI Assistant. I\'m here to help you with any questions about the hostel management system.',
        'Hi there! How can I assist you today?',
        'Welcome! Feel free to ask me anything about hostel management, complaints, leaves, fees, or anything else.',
    ],
    
    'help': [
        'I can help you with:\n• Filing and tracking complaints\n• Applying for leave\n• Viewing notices\n• Checking fees\n• Room information\n\nWhat would you like help with?',
        'You can ask me about complaints, leave requests, notices, fees, rooms, or hostel policies.',
    ],
    
    'contact': [
        'For urgent matters, please visit the admin office during office hours (9 AM - 5 PM, Monday to Friday).',
        'You can also reach out to the admin through the complaints section for formal inquiries.',
    ],
    
    'policy': [
        'For hostel policies, please check the notices section or contact the admin office.',
        'General policies are also explained during hostel orientation.',
    ],
    
    # Time-related
    'time': [
        f'Current time: {datetime.now().strftime("%I:%M %p")}',
    ],
}

def get_bot_response(user_message):
    """
    Generate a chatbot response based on user message
    Uses keyword matching to determine the appropriate response
    """
    message_lower = user_message.lower().strip()
    
    # Greeting responses
    if any(word in message_lower for word in ['hi', 'hello', 'hey', 'greetings']):
        return random.choice(CHATBOT_RESPONSES['hello'])
    
    # Help responses
    if 'help' in message_lower or '?' in message_lower and len(message_lower) < 20:
        return random.choice(CHATBOT_RESPONSES['help'])
    
    # Complaint related
    if any(word in message_lower for word in ['complaint', 'complain', 'issue', 'problem', 'broken', 'damage']):
        return random.choice(CHATBOT_RESPONSES['complaint'])
    
    # Leave related
    if any(word in message_lower for word in ['leave', 'absent', 'vacation', 'time off', 'off campus']):
        return random.choice(CHATBOT_RESPONSES['leave'])
    
    # Notice related
    if any(word in message_lower for word in ['notice', 'announcement', 'news', 'update']):
        return random.choice(CHATBOT_RESPONSES['notice'])
    
    # Fee related
    if any(word in message_lower for word in ['fee', 'payment', 'bill', 'charges', 'cost', 'price', 'expense']):
        return random.choice(CHATBOT_RESPONSES['fee'])
    
    # Room related
    if any(word in message_lower for word in ['room', 'accommodation', 'bed', 'dorm', 'hostel']):
        return random.choice(CHATBOT_RESPONSES['room'])
    
    # Contact related
    if any(word in message_lower for word in ['contact', 'call', 'phone', 'office', 'visit', 'reach']):
        return random.choice(CHATBOT_RESPONSES['contact'])
    
    # Policy related
    if 'policy' in message_lower or 'rule' in message_lower:
        return random.choice(CHATBOT_RESPONSES['policy'])
    
    # Time query
    if 'time' in message_lower:
        return random.choice(CHATBOT_RESPONSES['time'])
    
    # Default response
    default_responses = [
        'I\'m not sure about that specific topic. Could you rephrase your question? I can help with complaints, leave requests, notices, fees, rooms, or general hostel information.',
        'That\'s an interesting question! Could you be more specific? I can assist with:\n• Complaints\n• Leave Requests\n• Notices\n• Fees\n• Room Information\n• Hostel Policies',
        'I\'m still learning about that topic. Please contact the admin office for detailed information, or let me know if I can help with something else!',
        'Feel free to ask me about any hostel-related queries or navigate through the menu for specific information.',
    ]
    return random.choice(default_responses)

@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot_endpoint():
    """
    Handle chatbot API requests
    Expects JSON with 'message' field
    Returns JSON with 'response' field
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'response': 'Please provide a message.'
            }), 400
        
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'response': 'Message cannot be empty.'
            }), 400
        
        # Get bot response
        bot_response = get_bot_response(user_message)
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'An error occurred: {str(e)}'
        }), 500

@chatbot_bp.route('/chatbot-settings', methods=['GET'])
def get_chatbot_settings():
    """Get chatbot configuration settings"""
    return jsonify({
        'name': 'Hostel Assistant',
        'version': '1.0',
        'status': 'online',
        'features': [
            'Complaint tracking',
            'Leave request assistance',
            'Notice information',
            'Fee inquiries',
            'Room information',
            'General hostel policies'
        ]
    }), 200
