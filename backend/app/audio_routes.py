from flask import Blueprint, jsonify, request,send_from_directory,current_app,url_for, redirect
from flask_login import login_required, current_user
from app import db,config
from app.models import Meeting, Message
from datetime import datetime
import os
import uuid
import time

from app.fireflies import upload_video,get_admin_id,get_transcripts,get_transcript

bp = Blueprint('audio', __name__)

MAX_RETRIES =42  # Maximum times to check before giving up
RETRY_DELAY = 10  # Number of seconds to wait before retrying

MAX_ID_RETRIES = 42  # Max times to check for transcript ID
ID_RETRY_DELAY = 10  # Seconds to wait before retrying

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def wait_for_transcript_id(admin_id, meeting_title):
    """ Poll Fireflies to check if the transcript ID is available. """
    retries = 0
    transcript_id = None

    while retries < MAX_ID_RETRIES:
        print(f"Checking for transcript ID... Attempt {retries + 1}/{MAX_ID_RETRIES}")

        transcript_id = get_transcripts(admin_id, meeting_title)

        if transcript_id:  # If ID is found, return it
            print(f"Transcript ID found: {transcript_id}")
            return transcript_id

        # Wait before checking again
        time.sleep(ID_RETRY_DELAY)
        retries += 1

    print("Transcript ID not found after multiple attempts.")
    return None

#  Function to wait the transcript to be ready before continue sending any response to the frontend
def wait_for_transcript(transcript_id):
    """ Poll Fireflies to check if the transcript is ready. """
    retries = 0

    while retries < MAX_RETRIES:
        print(f"Checking transcript status... Attempt {retries + 1}/{MAX_RETRIES}")

        try:
            summary, full_transcript = get_transcript(transcript_id)

            # If transcript is available, return it
            if summary and full_transcript:
                print("Transcript is ready!")
                return summary, full_transcript

        except Exception as e:
            print("Error fetching transcript:", e)

        # Wait before checking again
        time.sleep(RETRY_DELAY)
        retries += 1

    print("Transcript not available after multiple attempts.")
    return None, None


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
        uploads_dir = current_app.config["UPLOAD_FOLDER"]

        # Ensure the directory exists
        os.makedirs(uploads_dir, exist_ok=True)


        # Construct the file name
        file_name = f"{timestamp}_{email}_{filename}".replace(" ","_")
        file_name = f"{timestamp}_{uuid.uuid4().hex}_{filename}".replace(" ", "_")

        # Full path to save the file
        file_path = os.path.join(uploads_dir, file_name)

        # Write the audio chunk to the file
        try:
            with open(file_path, 'wb') as f:
                f.write(audio_chunk)
        except IOError as e:
            print(f"Error writing file: {e}")
            return jsonify({"error": "File not saved"}), 500

        print('filename',file_name)

        
        # Get the base URL for ngrok from your configuration
        ngrok_base_url = "https://92bb-135-19-4-239.ngrok-free.app"  # Replace with your ngrok URL
        
        # Construct the full URL for the file
        url = f"{ngrok_base_url}/uploads/{file_name}"

        #Create a meeting title to reference it when needed
        meeting_title=file_name

        print("File url",url)
        print("File path",file_path)
        
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} was not saved correctly.")
            return jsonify({"error": "File not saved"}), 500
        
        # Upload video to fireflies for processing
        status,status_text=upload_video(url,meeting_title)
        if status==False:
            print(status_text)
            return jsonify({"error": status_text}), 500


        # Get the ID of the administrator
        admin_id=get_admin_id()

        # Get the id associated to the admin account  and the identifier of the actual meeting(MeetingId)
        transcript_id = wait_for_transcript_id(admin_id, meeting_title)

        if not transcript_id:
            return jsonify({"error": "Transcript ID not found after multiple attempts"}), 500

        print("\nWaiting for transcript to be ready...")
        summary, full_transcript = wait_for_transcript(transcript_id)

        if summary and full_transcript:
            print("\nTranscript successfully retrieved!")
        else:
            print("\nFailed to retrieve transcript.")

        # Delete the file after processing
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file: {e}")

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
    


# This route is essential because it provides access to the video using the url given to an external service
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    uploads_dir = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(uploads_dir, filename)

