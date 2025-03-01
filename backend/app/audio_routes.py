from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db,config
from app.models import Meeting, Message
import whisper
from transformers import T5Tokenizer, T5ForConditionalGeneration, pipeline, AutoModelForCausalLM, AutoTokenizer
import numpy as np
import librosa
import io
import os
import time
from werkzeug.utils import secure_filename



# Load the Whisper model (you can change to 'small', 'medium', 'large' based on your needs)
whisper_model = whisper.load_model("large")


bp = Blueprint('audio', __name__)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def transcribe_audio(audio_file):
    # Create a unique file name using timestamp or UUID
    unique_filename = f"{int(time.time())}_{current_user.email}_{secure_filename(audio_file.filename)}"


    # Instead of loading from the in-memory file, use the saved file path
    file_path = os.path.join('uploads', unique_filename)

    audio_file.save(file_path)

    # Transcribe the audio file
    result = whisper_model.transcribe(file_path)
    return result["text"]


# Route to upload an audio file and create a meeting if needed
@bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    audio_file = request.files['file']

    if audio_file.filename == '' or not allowed_file(audio_file.filename):
        return jsonify({"error": "Invalid file format"}), 400

    try:
        # Transcribe the uploaded audio
        transcript = transcribe_audio(audio_file)

        # Check if a meeting ID was provided
        meeting_id = request.form.get('meetingId')
        
        if not meeting_id:
            # Create a new meeting without a topic initially
            meeting = Meeting(
                user_id=current_user.id,  # Associate the meeting with the current user
                transcript=transcript,
                topic="Temporary"
            )
            
            # Add the meeting to the session and flush to get the meeting ID
            db.session.add(meeting)
            db.session.flush()

            # Set the topic using the meeting ID after it has been assigned
            meeting.topic = f"Meeting {meeting.id}"
        else:
            # Check if the meeting exists
            meeting = Meeting.query.get(meeting_id)
            if not meeting:
                return jsonify({'error': 'Meeting not found'}), 404

            # Check if the meeting is associated with the current user (if needed)
            if meeting.user_id != current_user.id:
                return jsonify({'error': 'You are not authorized to update this meeting'}), 403

            # Process the transcript, save it to the meeting
            meeting.transcript = transcript
        
        db.session.commit()

        # Get the messages related to the meeting
        user_messages = Message.query.filter_by(meeting_id=meeting.id, is_user=True).all()
        system_messages = Message.query.filter_by(meeting_id=meeting.id, is_user=False).all()

        # Format the messages
        user_message_data = [{
            "content": msg.content,
            "is_user": msg.is_user,
            "topic": msg.topic,
            "created_at": msg.created_at.isoformat()
        } for msg in user_messages]

        system_message_data = [{
            "content": msg.content,
            "is_user": msg.is_user,
            "topic": msg.topic,
            "created_at": msg.created_at.isoformat()
        } for msg in system_messages]

        return jsonify({
            "message": "File uploaded and transcript processed successfully",
            "meeting": {
                "id": meeting.id,
                "topic": meeting.topic,
                "transcript": meeting.transcript,
                "messages": user_message_data + system_message_data  # Combine both user and system messages
            }
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500




