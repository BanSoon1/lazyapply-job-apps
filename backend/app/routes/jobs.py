from flask import Blueprint, request, jsonify
from app.services.job_service import search_jobs

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")


@jobs_bp.get("/search")
def search():
    result = search_jobs(
        query    = request.args.get("q",         "").strip(),
        location = request.args.get("location",  "").strip(),
        job_type = request.args.get("jobType",   "").strip(),
        sal_min  = request.args.get("salaryMin", "").strip(),
    )
    return jsonify(result), 200


@jobs_bp.get("/<int:job_id>")
def get_job(job_id):
    from app.models.job import Job
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({"job": job.to_dict()}), 200