from app.extensions import db


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    job_id  = db.Column(db.Integer, db.ForeignKey("jobs.job_id"),   nullable=False)

    user = db.relationship("User", back_populates="saved_jobs")
    job  = db.relationship("Job",  back_populates="saved_by")

    def to_dict(self):
        return {
            "id":      self.id,
            "user_id": self.user_id,
            "job":     self.job.to_dict() if self.job else None,
        }