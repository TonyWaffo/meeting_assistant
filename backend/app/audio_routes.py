from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import wave
import numpy as np
from app import db
from app.models import Meeting, Message
import pyaudio
import whisper
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

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

def save_chunk_to_file(audio_chunk):
    """Saves an audio chunk to a WAV file for processing."""
    with wave.open(TEMP_AUDIO_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(audio_chunk)

def transcribe_audio(audio_chunk):
    """Transcribes an audio chunk using Whisper."""
    save_chunk_to_file(audio_chunk)
    segments, _ = whisper_model.transcribe(TEMP_AUDIO_FILE)
    return " ".join(segment.text for segment in segments)

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

    # Transcribe the uploaded audio
    transcript = transcribe_audio(audio_chunk)

    # Deriving the topic from the first few words of the transcript
    topic = " ".join(transcript.split()[:5])  # First 5 words as topic (you can adjust this logic)

    # Create a new meeting in the database
    new_meeting = Meeting(
        topic=topic,
        transcript=transcript,
        user_id=current_user.id  # Assuming the user is logged in and you want to associate the meeting with the current user
    )

    # Add the meeting to the session and commit to save it in the database
    db.session.add(new_meeting)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully", "transcript": transcript, "meeting_id": new_meeting.id}), 200

# Route to send a question and get an answer based on the transcribed text
@bp.route('/answer', methods=['POST'])
@login_required
def answer():
    data = request.get_json()
    question = data.get('question')  # Question from the user
    meeting_id = data.get('meeting_id')  # Meeting ID from the user

    if not question or not meeting_id:
        return jsonify({"error": "Both question and meeting_id are required"}), 400

    # Fetch the meeting transcript from the database using the meeting_id
    meeting = Meeting.query.get(meeting_id)
    
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    transcript = meeting.transcript  # Assuming 'transcript' is a column in the Meeting model
    
    if not transcript:
        return jsonify({"error": "Transcript not available for this meeting"}), 404

    # Generate the answer based on the transcript and question
    answer_text = answer_question(transcript, question)
    
    return jsonify({"answer": answer_text}), 200


