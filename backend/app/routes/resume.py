import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.resume import Resume
from app.services.resume_service import process_resume

resume_bp = Blueprint("resume", __name__, url_prefix="/api/resume")

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@resume_bp.post("/")
@jwt_required()
def upload_resume():
    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF, DOC, and DOCX files are allowed"}), 400

    upload_folder = os.path.join(current_app.root_path, "..", "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    filename  = secure_filename(f"user_{user_id}_{file.filename}")
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    # Remove old resume if exists
    existing = Resume.query.filter_by(user_id=user_id).first()
    if existing:
        db.session.delete(existing)

    resume = Resume(user_id=user_id, file_path=file_path)
    db.session.add(resume)
    db.session.commit()

    # Extract skills from the uploaded file
    process_resume(resume)

    return jsonify({"message": "Resume uploaded", "resume": resume.to_dict()}), 201


@resume_bp.get("/")
@jwt_required()
def get_resume():
    user_id = int(get_jwt_identity())
    resume  = Resume.query.filter_by(user_id=user_id).first()

    if not resume:
        return jsonify({"error": "No resume found"}), 404

    return jsonify({"resume": resume.to_dict()}), 200