from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db, Note
from utils import verify_signature, is_valid_ethereum_address
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/notes', methods=['GET'])
def get_notes():
    wallet = request.args.get('wallet_address')
    if not wallet or not is_valid_ethereum_address(wallet):
        return jsonify({"error": "Invalid or missing wallet address"}), 400

    notes = Note.query.filter_by(author=wallet.lower()).all()
    return jsonify({"notes": [note.to_dict() for note in notes]}), 200

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    author = data.get("author")
    signature = data.get("signature")
    message = data.get("message")

    if not all([title, content, author, signature, message]):
        return jsonify({"error": "Missing fields"}), 400

    if not is_valid_ethereum_address(author):
        return jsonify({"error": "Invalid Ethereum address"}), 400

    if not verify_signature(message, signature, author):
        return jsonify({"error": "Invalid signature"}), 403

    note = Note(title=title, content=content, author=author.lower())
    db.session.add(note)
    db.session.commit()

    return jsonify(note.to_dict()), 201

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    wallet = request.args.get('wallet_address')
    note = Note.query.get_or_404(note_id)

    if not wallet or note.author != wallet.lower():
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify(note.to_dict()), 200

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.get_json()
    note = Note.query.get_or_404(note_id)

    author = data.get("author")
    signature = data.get("signature")
    message = data.get("message")

    if note.author != author.lower():
        return jsonify({"error": "Unauthorized"}), 403

    if not verify_signature(message, signature, author):
        return jsonify({"error": "Invalid signature"}), 403

    note.title = data.get("title", note.title)
    note.content = data.get("content", note.content)
    db.session.commit()

    return jsonify(note.to_dict()), 200

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    data = request.get_json()
    note = Note.query.get_or_404(note_id)

    author = data.get("author")
    signature = data.get("signature")
    message = data.get("message")

    if note.author != author.lower():
        return jsonify({"error": "Unauthorized"}), 403

    if not verify_signature(message, signature, author):
        return jsonify({"error": "Invalid signature"}), 403

    db.session.delete(note)
    db.session.commit()

    return jsonify({"message": "Note deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)
