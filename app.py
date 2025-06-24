
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Note
from utils import verify_signature, is_valid_ethereum_address
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
CORS(app)

# ✅ Ensure tables are created (SQLite-compatible on Render)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "Notebook Flask backend running!", 200

@app.route("/api/notes", methods=["GET"])
def get_notes():
    wallet = request.args.get("wallet_address")
    if not wallet or not is_valid_ethereum_address(wallet):
        return jsonify({"error": "Invalid or missing wallet address"}), 400

    notes = Note.query.filter_by(author=wallet.lower()).all()
    return jsonify({"notes": [n.to_dict() for n in notes]}), 200

@app.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    required = ["title", "content", "author", "signature", "message"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    if not verify_signature(data["message"], data["signature"], data["author"]):
        return jsonify({"error": "Invalid signature"}), 403

    note = Note(
        title=data["title"],
        content=data["content"],
        author=data["author"].lower()
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201

@app.route("/api/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    wallet = request.args.get("wallet_address")
    note = Note.query.get_or_404(note_id)
    if note.author != wallet.lower():
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(note.to_dict()), 200

@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json()
    note = Note.query.get_or_404(note_id)

    if note.author != data.get("author", "").lower():
        return jsonify({"error": "Unauthorized"}), 403

    # if not verify_signature(data["message"], data["signature"], data["author"]):
    #     return jsonify({"error": "Invalid signature"}), 403

    note.title = data.get("title", note.title)
    note.content = data.get("content", note.content)
    db.session.commit()
    return jsonify(note.to_dict()), 200

@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    data = request.get_json()
    note = Note.query.get_or_404(note_id)

    if note.author != data.get("author", "").lower():
        return jsonify({"error": "Unauthorized"}), 403

    if not verify_signature(data["message"], data["signature"], data["author"]):
        return jsonify({"error": "Invalid signature"}), 403

    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted"}), 200

if __name__ == "__main__":
    app.run()