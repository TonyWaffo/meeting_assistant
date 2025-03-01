from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Meeting, Message
from app import db
from transformers import T5Tokenizer, T5ForConditionalGeneration, pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
import os

import openai

# OpenAI API Key
OPENAI_API_KEY= "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"


client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Create an OpenAI client instance

# # Dynamically select the device (GPU, VPU, or CPU)
# if torch.cuda.is_available():
#     device = "cuda"  # Use GPU if available
# elif torch.backends.mps.is_available():  # For Apple Silicon devices (M1, M2) with VPU support
#     device = "mps"  # Use VPU if available
# else:
#     device = "cpu"  # Default to CPU if neither GPU nor VPU is available


HUGGINGFACE_TOKEN='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'

# Load a pre-trained conversational model (Llama)
# model_name = "mistralai/Mistral-7B-Instruct-v0.2"
# tokenizer = AutoTokenizer.from_pretrained(model_name,token=HUGGINGFACE_TOKEN)
# qa_model = AutoModelForCausalLM.from_pretrained(model_name,token=HUGGINGFACE_TOKEN)

bp = Blueprint('main', __name__)


# def answer_question(context, question):
#     # Format the input for the model: context followed by the question
#     prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"

#     # Tokenize the prompt and prepare inputs
#     inputs = tokenizer(prompt, return_tensors="pt").to(device)

#     # Generate a response from the model
#     generated_ids = qa_model.generate(inputs["input_ids"], max_new_tokens=1000, do_sample=True)

#     # Decode the generated response
#     generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

#     # Return the response
#     return generated_text

def answer_question(context, question):
    """Use OpenAI's GPT-4 API to answer the question based on the context."""
    prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content  # New response format
    except Exception as e:
        return f"Error: {e}"


# Route to get all meetings of the current user
@bp.route('/meetings', methods=['GET'])
@login_required
def get_meetings():
    meetings = current_user.meetings.all()
    return jsonify([{"id": m.id, "topic": m.topic, "transcript":m.transcript} for m in meetings]), 200

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


# Send message after creating a meeting (if it doesn't exist) or send a message to an existing meeting
@bp.route('/meeting/message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    content = data.get('content')  # Get the content of the message
    meeting_id = data.get('meeting_id')  # Get the meeting ID (optional, if existing meeting)
    topic = data.get('topic', 'question_answer')  # Get the topic of the message (defaults to 'question_answer' if not provided)

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
        meeting = Meeting(topic="Temporary", user_id=current_user.id)
        db.session.add(meeting)
        db.session.flush()  # This assigns an ID before committing

        # # Get current date and time
        # now = datetime.now()
        # formatted_datetime = now.strftime("%-d-%d-%m-%Y_%H:%M")  # Format: d-dd-mm-yyyy_hh:mm

        # Set the topic to the meeting ID
        meeting.topic = f"Meeting {meeting.id}"

        db.session.commit()

    # Create a new message from the user in the (new or existing) meeting
    user_message = Message(content=content, is_user=True, topic=topic, meeting_id=meeting.id)
    db.session.add(user_message)
    

    # Generate the answer based on the transcript and question
    transcript = meeting.transcript or ""
    answer_text = answer_question(transcript, content)

    # Store AI response
    system_message = Message(content=answer_text, is_user=False, topic="transcription", meeting_id=meeting.id)
    db.session.add(system_message)
    
    db.session.commit()  # Commit both the message and the system reply

    return jsonify({
        "message": "Message sent successfully",
        "meeting": {
            "id": meeting.id,
            "topic": meeting.topic,
            "transcript": meeting.transcript,
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