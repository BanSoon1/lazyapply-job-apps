from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.saved_job import SavedJob
from app.models.job import Job

saved_jobs_bp = Blueprint("saved_jobs", __name__, url_prefix="/api/saved-jobs")


@saved_jobs_bp.post("/")
@jwt_required()
def save_job():
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True) or {}
    job_id  = data.get("job_id")

    if not job_id:
        return jsonify({"error": "job_id is required"}), 400

    if not Job.query.get(job_id):
        return jsonify({"error": "Job not found"}), 404

    already_saved = SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first()
    if already_saved:
        return jsonify({"error": "Job already saved"}), 409

    saved = SavedJob(user_id=user_id, job_id=job_id)
    db.session.add(saved)
    db.session.commit()

    return jsonify({"message": "Job saved", "saved_job": saved.to_dict()}), 201


@saved_jobs_bp.get("/")
@jwt_required()
def get_saved_jobs():
    user_id    = int(get_jwt_identity())
    saved_jobs = SavedJob.query.filter_by(user_id=user_id).all()
    return jsonify({"saved_jobs": [s.to_dict() for s in saved_jobs]}), 200


@saved_jobs_bp.delete("/<int:saved_id>")
@jwt_required()
def delete_saved_job(saved_id):
    user_id = int(get_jwt_identity())
    saved   = SavedJob.query.filter_by(id=saved_id, user_id=user_id).first()

    if not saved:
        return jsonify({"error": "Saved job not found"}), 404

    db.session.delete(saved)
    db.session.commit()
    return jsonify({"message": "Saved job removed"}), 200