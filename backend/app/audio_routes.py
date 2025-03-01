from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db,config
from app.models import Meeting, Message
from datetime import datetime
import os

from app.fireflies import upload_video,get_admin_id,get_transcripts,get_transcript

bp = Blueprint('audio', __name__)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route to upload an audio file, transcribe it, and create a meeting
@bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']

        email = current_user.email  # Replace with how you access the current user's email

        # Assume 'file' is your audio file object and it has the 'filename' attribute
        filename = file.filename

        # Assume 'file' is your audio file object and 'email' and 'name' are provided
        audio_chunk = file.read()

        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define the directory for saving files
        uploads_dir = 'uploads/'

        # Ensure the directory exists
        os.makedirs(uploads_dir, exist_ok=True)


        # Construct the file name
        file_name = f"{timestamp}_{email}_{filename}"

        # Full path to save the file
        file_path = os.path.join(uploads_dir, file_name)

        # Write the audio chunk to the file
        with open(file_path, 'wb') as f:
            f.write(audio_chunk)

        # Now the file is saved in the uploads folder with the required timestamp, email, and name
        url = f'https://92bb-135-19-4-239.ngrok-free.app/{file_path}'  # This is the path to the uploaded fi
        
        #Create a meeting title to reference it when needed
        meeting_title=file_name

        print(url)
        # Upload video to fireflies for processing
        upload_video(url,meeting_title)

        # Get the ID of the administrator
        admin_id=get_admin_id()

        # Get the id associated to the admin account  and the identifier of the actual meeting(MeetingId)
        # transcript_id=get_transcripts(admin_id,meeting_title)
        transcript_id=get_transcripts(admin_id,"Meeting test")

        print(transcript_id)

        print("\nGetting  a special transcript....")
        summary,full_transcript=get_transcript(transcript_id)

        print(full_transcript)

        # Deriving the topic from the first few words of the transcript
        topic = " ".join(full_transcript.split()[:5])  # First 5 words as topic (you can adjust this logic)

        # Create a new meeting in the database
        new_meeting = Meeting(
            topic=topic,
            transcript=full_transcript,
            user_id=current_user.id  # Assuming the user is logged in and you want to associate the meeting with the current user
        )

        # Add the meeting to the session and commit to save it in the database
        db.session.add(new_meeting)
        db.session.commit()

        # Retrieve related messages
        user_messages = Message.query.filter_by(meeting_id=new_meeting.id, is_user=True).all()
        system_messages = Message.query.filter_by(meeting_id=new_meeting.id, is_user=False).all()

        # Format messages for response
        format_message = lambda msg: {
            "content": msg.content,
            "is_user": msg.is_user,
            "topic": msg.topic,
            "created_at": msg.created_at.isoformat()
        }

        user_message_data = [format_message(msg) for msg in user_messages]
        system_message_data = [format_message(msg) for msg in system_messages]

        return jsonify({
                "message": "File uploaded and transcript processed successfully",
                "meeting": {
                    "id": new_meeting.id,
                    "topic": new_meeting.topic,
                    "transcript": new_meeting.transcript,
                    "messages": user_message_data + system_message_data
                }
            }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500




