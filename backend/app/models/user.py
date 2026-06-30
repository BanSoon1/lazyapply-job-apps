from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    user_id            = db.Column(db.Integer, primary_key=True)
    name               = db.Column(db.String(120), nullable=False)
    email              = db.Column(db.String(200), unique=True, nullable=False)
    password_hash      = db.Column(db.String(256), nullable=False)
    preferred_location = db.Column(db.String(120))
    preferred_job_type = db.Column(db.String(80))

    resumes     = db.relationship("Resume",   back_populates="user", lazy=True)
    saved_jobs  = db.relationship("SavedJob", back_populates="user", lazy=True)

    def to_dict(self):
        return {
            "user_id":            self.user_id,
            "name":               self.name,
            "email":              self.email,
            "preferred_location": self.preferred_location,
            "preferred_job_type": self.preferred_job_type,
        }