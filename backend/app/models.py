from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
import tiktoken  # Ensure you have installed tiktoken (pip install tiktoken)
from bs4 import BeautifulSoup

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meetings = db.relationship('Meeting', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255))
    transcript = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    messages = db.relationship('Message', backref='meeting', lazy='dynamic')

    def get_transcript_chunks_by_tokens(self, max_tokens=300, model_name="gpt-3.5-turbo"):
        """
        Splits the transcript into chunks where each chunk has no more than max_tokens tokens.
        It splits on sentence boundaries to keep the text coherent.
        """
        # Create an encoder for the model
        encoding = tiktoken.encoding_for_model(model_name)
        
        # Split transcript into sentences using a simple regex
        sentences = re.split(r'(?<=[.!?])\s+', self.transcript)
        chunks = []
        current_chunk = ""
        current_token_count = 0

        for sentence in sentences:
            # Count tokens for the sentence
            sentence_token_count = len(encoding.encode(sentence))
            
            # If adding this sentence exceeds the max token limit, save the current chunk and reset
            if current_token_count + sentence_token_count > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
                current_token_count = sentence_token_count
            else:
                # Append the sentence to the current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_token_count += sentence_token_count

        # Add any remaining text as the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
    
    def get_transcript_chunks_by_characters(self, max_characters=5000):
        """
        Splits the transcript into chunks where each chunk has no more than max_characters characters.
        It splits on sentence boundaries to keep the text coherent.
        """
        # Split transcript into sentences using a simple regex
        sentences = re.split(r'(?<=[.!?])\s+', self.transcript)
        soup = BeautifulSoup(self.transcript, 'html.parser')
        example = soup.get_text()
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', example)
        chunks = []
        current_chunk = ""
        current_char_count = 0

        for sentence in sentences:
            # Count characters for the sentence
            sentence_char_count = len(sentence)
            
            # If adding this sentence exceeds the max character limit, save the current chunk and reset
            if current_char_count + sentence_char_count > max_characters:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
                current_char_count = sentence_char_count
            else:
                # Append the sentence to the current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_char_count += sentence_char_count

        # Add any remaining text as the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    is_user = db.Column(db.Boolean)
    topic = db.Column(db.Enum('transcription', 'summary', 'question_answer', name='message_topic'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
