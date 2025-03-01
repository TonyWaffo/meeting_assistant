from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db,config
from app.models import Meeting, Message
import whisper
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

from fireflies import upload_video,get_admin_id,get_transcripts,get_transcript

# Initialize models
device = "cuda" if torch.cuda.is_available() else "cpu"
whisper_model = whisper.load_model("small",device=device)
tokenizer = T5Tokenizer.from_pretrained("t5-small")
qa_model = T5ForConditionalGeneration.from_pretrained("t5-small")

# Audio Settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
FRAME_DURATION = 10
FRAME_SIZE = int(RATE * FRAME_DURATION / 1000)
TEMP_AUDIO_FILE = "temp_audio_chunk.wav"

# Initialize PyAudio
audio = pyaudio.PyAudio()

bp = Blueprint('audio', __name__)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def answer_question(context, question):
    """Generates an answer based on transcribed text using T5 model."""
    prompt = f"question: {question}  context: {context}"
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    output = qa_model.generate(**inputs, max_length=100)
    return tokenizer.decode(output[0], skip_special_tokens=True)


# Route to upload an audio file, transcribe it, and create a meeting
@bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    audio_chunk = file.read()

    # Save video to the google drive or the server

    # Grab the url of the video saved in the server
    url=''

    # Upload video to fireflies for processing
    upload_video(url)

    # Get the ID of the administrator
    admin_id=get_admin_id()

    #Create a meeting ID
    meeting_id="Meeting test"

    # Get the id associated to the admin account  and the identifier of the actual meeting(MeetingId)
    transcript_id=get_transcripts(admin_id,meeting_id)

    print("\nGeting  a special transcript....")
    summary,full_transcript=get_transcript(transcript_id)

    full_transcript

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




