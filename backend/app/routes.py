from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Meeting, Message
from app import db

bp = Blueprint('main', __name__)

# Route to get all meetings of the current user
@bp.route('/meetings', methods=['GET'])
@login_required
def get_meetings():
    meetings = current_user.meetings.all()
    return jsonify([{"id": m.id, "topic": m.topic} for m in meetings]), 200

# Route to get details of a specific meeting, including messages with created_at
@bp.route('/meeting/<int:meeting_id>', methods=['GET'])
@login_required
def get_meeting(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    if meeting.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    messages = meeting.messages.all()
    return jsonify({
        "id": meeting.id,
        "topic": meeting.topic,
        "transcript": meeting.transcript,
        "messages": [{
            "content": m.content,
            "is_user": m.is_user,
            "created_at": m.created_at.isoformat()  # Add created_at in ISO format
        } for m in messages]
    }), 200

# Route to upload a file (e.g., a meeting transcript)
@bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    # Process the file and extract transcript
    # For now, just return a placeholder
    return jsonify({"message": "File uploaded successfully", "transcript": "Sample transcript"}), 200

# Route to send a message in a specific meeting, and automatically reply with a system message
@bp.route('/meeting/<int:meeting_id>/message', methods=['POST'])
@login_required
def send_message(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({"error": "Message content is required"}), 400
    
    # Create a new message from the user and associate it with the meeting
    user_message = Message(content=content, is_user=True, meeting_id=meeting.id)
    db.session.add(user_message)
    db.session.commit()

    # Create an automatic reply message from the system
    system_message = Message(content="Message received, thank you!", is_user=False, meeting_id=meeting.id)
    db.session.add(system_message)
    db.session.commit()

    return jsonify({
        "message": "Message sent and system reply added successfully",
        "user_message": {
            "content": user_message.content,
            "created_at": user_message.created_at.isoformat()
        },
        "system_reply": {
            "content": system_message.content,
            "created_at": system_message.created_at.isoformat()
        }
    }), 201
