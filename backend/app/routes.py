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
            "topic":    m.topic,
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

# Send message after creating a meeting (if it doesn't exist) or send a message to an existing meeting
@bp.route('/meeting/message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    content = data.get('content')  # Get the content of the message
    meeting_id = data.get('meeting_id')  # Get the meeting ID (optional, if existing meeting)
    topic = data.get('topic', 'transcription')  # Get the topic of the message (defaults to 'transcription' if not provided)

    if not content:
        return jsonify({"error": "Message content is required"}), 400

    if meeting_id:
        # If a meeting ID is provided, try to find the meeting
        meeting = Meeting.query.get(meeting_id)
        if not meeting:
            return jsonify({"error": "Meeting not found"}), 404
        if meeting.user_id != current_user.id:
            return jsonify({"error": "Unauthorized"}), 403
    else:
        # If no meeting ID is provided, create a new meeting
        meeting = Meeting(topic="New Meeting", user_id=current_user.id)
        db.session.add(meeting)
        db.session.commit()  # Save the meeting to get an ID

    # Create a new message from the user in the (new or existing) meeting
    user_message = Message(content=content, is_user=True, topic=topic, meeting_id=meeting.id)
    db.session.add(user_message)
    
    # Optional: Add an automatic system reply
    system_message = Message(content="Message received, thank you!", is_user=False, topic="transcription", meeting_id=meeting.id)
    db.session.add(system_message)
    
    db.session.commit()  # Commit both the message and the system reply

    return jsonify({
        "message": "Message sent successfully",
        "meeting": {
            "id": meeting.id,
            "topic": meeting.topic,
            "messages": [{
                "content": user_message.content,
                "is_user": user_message.is_user,
                "topic": user_message.topic,
                "created_at": user_message.created_at.isoformat()
            }, {
                "content": system_message.content,
                "is_user": system_message.is_user,
                "topic": system_message.topic,
                "created_at": system_message.created_at.isoformat()
            }]
        }
    }), 201
