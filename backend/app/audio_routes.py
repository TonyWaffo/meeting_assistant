from flask import Blueprint, jsonify, request,send_from_directory,current_app,url_for, redirect
from flask_login import login_required, current_user
from app import db,config
from app.models import Meeting, Message
from datetime import datetime,timedelta
import os
import uuid
import time
from moviepy.video.io.VideoFileClip import VideoFileClip

from app.fireflies import upload_media,get_admin_id,get_transcripts,get_transcript

bp = Blueprint('audio', __name__)

MAX_RETRIES =60  # Maximum times to check before giving up
RETRY_DELAY = 10  # Number of seconds to wait before retrying

MAX_ID_RETRIES = 60  # Max times to check for transcript ID
ID_RETRY_DELAY = 10  # Seconds to wait before retrying

ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'wav', 'ogg', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_video_to_audio(input_video, output_audio):
    try:
        video = VideoFileClip(input_video)
        if video.audio:
            video.audio.write_audiofile(output_audio, bitrate="192k")
            print(f"Conversion successful: {output_audio}")
            return output_audio
        else:
            print("Error: No audio found in the video.")
            return None
    except Exception as e:
        print(f"Error during conversion: {e}")
        return None
    

def cleanup_old_files():
    """Remove files older than 30 minutes."""
    expiration_time = datetime.now() - timedelta(minutes=30)
    uploads_dir = current_app.config["UPLOAD_FOLDER"]
    
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        try:
            if os.path.isfile(file_path):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mtime < expiration_time:
                    os.remove(file_path)
                    print(f"Deleted expired file: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


# tjis function is called periodically by the thread in the initialization file
def run_cleanup_periodically():
    while True:
        cleanup_old_files()
        time.sleep(1800)  # Run every 1800s=30min



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


def remove_file(file_path):
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")


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

        # Define the directory for saving files
        uploads_dir = current_app.config["UPLOAD_FOLDER"]

        if not allowed_file(filename):
            return jsonify({"error": "Invalid file format"}), 400
        

        # Ensure the directory exists
        os.makedirs(uploads_dir, exist_ok=True)

        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Construct the file name
        # file_name = f"{timestamp}_{email}_{filename}".replace(" ","_")
        file_name = f"{timestamp}_{uuid.uuid4().hex}_{filename}".replace(" ", "_")

        # Full path to save the file
        file_path = os.path.join(uploads_dir, file_name)

        try:
            # Save the file to disk
            file.save(file_path)
            print(f"File saved successfully at {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")
            return jsonify({"error": "File not saved"}), 500
        
        output_audio_path=''

        if filename.lower().endswith('.mp4'):  # Check if it's a video and needs conversion
            input_video_path = file_path
            output_audio_name = f"{os.path.splitext(file_name)[0]}.mp3"
            output_audio_path = os.path.join(uploads_dir, output_audio_name)
                
            # Perform the conversion and update filename
            converted_filename = convert_video_to_audio(input_video_path, output_audio_path)
            
            if not converted_filename:
                return jsonify({"error": "Error during video to audio conversion"}), 500

            # Update file_name to the new audio file name (take the last part of the path)
            file_name = os.path.basename(converted_filename)  # Only the last part of the path (filename)

        print('File name: ',file_name)

        
        # Get the base URL for ngrok from your configuration
        server_url = os.getenv('SERVER_URL')
        print(server_url)
        
        # Construct the full URL for the file
        url = f"{server_url}/uploads/{file_name}"

        #Create a meeting title to reference it when needed
        meeting_title=file_name

        print("File url: ",url)
        print("File path: ",file_path)
        if output_audio_path:
            print("Converted path: ",output_audio_path)
        
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} was not saved correctly.")
            return jsonify({"error": "File not saved"}), 500
        
        # Upload video to fireflies for processing
        status,status_text=upload_media(url,meeting_title)
        if status==False:
            # print(status_text)
            return jsonify({"error": status_text}), 500


        # Get the ID of the administrator
        admin_id=get_admin_id()

        # Get the id associated to the admin account  and the identifier of the actual meeting(MeetingId)
        transcript_id = wait_for_transcript_id(admin_id, meeting_title)

        if not transcript_id:
            return jsonify({"error": "Transcript ID not found after multiple attempts"}), 500

        print("\nWaiting for transcript to be ready...")
        summary, full_transcript = wait_for_transcript(transcript_id)

        # 01JNDFPYP9KD5N9BY8JCNR42PV

        if summary and full_transcript:
            print("\nTranscript successfully retrieved!")
        else:
            print("\nFailed to retrieve transcript.")

        # Delete the file after processing
        if output_audio_path:
            remove_file(output_audio_path)

        remove_file(file_path)

        # Create a new meeting in the database
        new_meeting = Meeting(
            topic="Meeting",  # Temporary placeholder topic
            transcript=full_transcript,
            user_id=current_user.id  # Assuming the user is logged in and you want to associate the meeting with the current user
        )

        # Add the meeting to the session and commit to save it in the database
        db.session.add(new_meeting)
        db.session.commit()

        # Now that the meeting has an id, update the topic
        new_meeting.topic = f"Meeting {new_meeting.id}"

        # Commit again to save the updated topic
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
        remove_file(output_audio_path)
        return jsonify({"error": str(e)}), 500
    
    


# This route is essential because it provides access to the video using the url given to an external service
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    uploads_dir = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(uploads_dir, filename)

