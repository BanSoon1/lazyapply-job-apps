from app.extensions import db


class Resume(db.Model):
    __tablename__ = "resumes"

    resume_id            = db.Column(db.Integer, primary_key=True)
    user_id              = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    file_path            = db.Column(db.String(500), nullable=False)
    extracted_skills     = db.Column(db.Text)   # stored as JSON string
    extracted_experience = db.Column(db.Text)   # stored as JSON string

    user = db.relationship("User", back_populates="resumes")

    def to_dict(self):
        return {
            "resume_id":            self.resume_id,
            "user_id":              self.user_id,
            "file_path":            self.file_path,
            "extracted_skills":     self.extracted_skills,
            "extracted_experience": self.extracted_experience,
        }