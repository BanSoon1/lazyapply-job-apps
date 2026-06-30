from app.models.user import User
from app.models.job import Job
from app.models.resume import Resume


def get_recommendations(user_id: int):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    jobs = Job.query.all()
    if not jobs:
        return {"recommendations": [], "message": "No jobs available"}, 200

    resume = Resume.query.filter_by(user_id=user_id).first()
    skills = _parse_skills(resume.extracted_skills if resume else None)

    scored = []
    for job in jobs:
        score = _score_job(job, user, skills)
        scored.append({**job.to_dict(), "match_score": score})

    scored.sort(key=lambda j: j["match_score"], reverse=True)
    top = scored[:10]

    return {"recommendations": top, "count": len(top)}, 200


def _parse_skills(extracted_skills: str | None) -> list[str]:
    if not extracted_skills:
        return []
    import json
    try:
        return json.loads(extracted_skills)
    except (ValueError, TypeError):
        return []


def _score_job(job: Job, user: User, skills: list[str]) -> int:
    score = 0

    # Location match
    if user.preferred_location and job.location:
        if user.preferred_location.lower() in job.location.lower():
            score += 40

    # Job type match
    if user.preferred_job_type and job.job_type:
        if user.preferred_job_type.lower() == job.job_type.lower():
            score += 30

    # Skills match against job description
    if skills and job.description:
        description_lower = job.description.lower()
        matched = sum(1 for skill in skills if skill.lower() in description_lower)
        score += matched * 10

    return score