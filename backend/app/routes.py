from flask import Blueprint, jsonify, request,current_app
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Meeting, Message
from app import db
import os
import json
import http.client
import openai
import ollama

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_URL=os.getenv("OLLAMA_URL")


client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Create an OpenAI client instance


bp = Blueprint('main', __name__)

# Answer question with the Open AI version 
# def answer_question(context, question):
#     """Use OpenAI's GPT-4 API to answer the question based on the context."""
#     prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
#     messages=[{"role": "user", "content": prompt}]
#     messages.append({
#         "role":"user",
#         "content":"Please ensure  the response is formated in the requested format and language mentionned in the prompt. Include approrpiate tags based on the format and return the respone in a single '' since it will be put together as html"
#     })
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=messages,
#             temperature=0.2,
#         )
#         print(response.choices[0].message.content)
#         return response.choices[0].message.content  # New response format
#     except Exception as e:
#         return f"Error: {e}"

# Answer question with the old ollama version
# def answer_question(context, question):
#     """Use OpenAI's GPT-4 API to answer the question based on the context."""
#     prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
#     messages = [
#         {"role": "system", "content": "You are an AI assistant responding based on the given conversation transcript."},
#         {"role": "user", "content": f"Here is the conversation transcript:\n{context}\n\nNow, respond to this: {question}"}
#     ]
#     messages.append({
#         "role":"user",
#         "content":"Please ensure  the response is formated in the requested format and language mentionned in the prompt. Include approrpiate tags based on the format and return the respone in a single '' since it will be put together as html"
#     })
#     try:
#         response = ollama.chat(model="mistral:7b-instruct", messages=messages)
#         return response['message']['content']
#     except Exception as e:
#         return f"Error: {e}"

# Answer question with the new Ollama version 
def answer_question(context,question):
    try:
        # Configuration de la connexion
        conn = http.client.HTTPSConnection(OLLAMA_URL)
        
        prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
        # Préparation des données de la requête
        payload = json.dumps({
            "model": "mistral:latest",
            "prompt": prompt,
            "options": {
                "max_tokens": 1000
            },
        })
        
        # En-têtes de la requête
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Envoi de la requête
        conn.request("POST", "/api/generate", payload, headers)
        # Obtention de la réponse
        response = conn.getresponse()
        
        # Lecture et traitement des données
        if response.status == 200:
            full_text = ""
            while True:
                chunk = response.readline()  # Read line by line
                if not chunk:
                    break
                try:
                    data = json.loads(chunk.decode("utf-8"))  # Parse JSON
                    if "response" in data:
                        full_text += data["response"]  # Append chunk
                    if data.get("done"):  # Stop when "done": true
                        break
                except json.JSONDecodeError:
                    continue  # Ignore partial or invalid chunks
            
            print("Full Response:", full_text)
            return full_text
        else:
            print(f"Erreur: {response.status} {response.reason}")
            return None
            
    except json.JSONDecodeError:
        print("Erreur: La réponse n'est pas au format JSON valide")
        return None
    except http.client.HTTPException as e:
        print(f"Erreur HTTP: {e}")
        return None
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return None
    finally:
        # Fermeture de la connexion
        if 'conn' in locals():
            conn.close()




# Route to get all meetings of the current user in
@bp.route('/meetings', methods=['GET'])
@login_required
def get_meetings():
    meetings = current_user.meetings.order_by(Meeting.id.desc()).all()
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
    # Retrieve transcript chunks using the method defined in your Meeting model.
    # transcript_chunks = meeting.get_transcript_chunks_by_tokens()  
    transcript_chunks=meeting.transcript

    # Process each chunk with answer_question and collect the responses.
    # answers = [answer_question(chunk, content) for chunk in transcript_chunks]
    answers=answer_question(transcript_chunks,content)

    # Combine the answers into one final response.
    # final_answer_text = "\n".join(answers)
    final_answer_text = answers
    

    # Store AI response
    system_message = Message(content=final_answer_text, is_user=False, topic="transcription", meeting_id=meeting.id)
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