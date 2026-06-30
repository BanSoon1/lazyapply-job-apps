from app.extensions import db


class Job(db.Model):
    __tablename__ = "jobs"

    job_id          = db.Column(db.Integer, primary_key=True)
    title           = db.Column(db.String(200), nullable=False)
    company         = db.Column(db.String(200), nullable=False)
    location        = db.Column(db.String(200))
    salary          = db.Column(db.String(100))
    job_type        = db.Column(db.String(80))
    description     = db.Column(db.Text)
    source_platform = db.Column(db.String(80))
    source_url      = db.Column(db.String(500))
    posted_label    = db.Column(db.String(80))

    saved_by = db.relationship("SavedJob", back_populates="job", lazy=True)

    def to_dict(self):
        return {
            "job_id":          self.job_id,
            "title":           self.title,
            "company":         self.company,
            "location":        self.location,
            "salary":          self.salary,
            "job_type":        self.job_type,
            "description":     self.description,
            "source_platform": self.source_platform,
            "source_url":      self.source_url,
            "posted_label":    self.posted_label,
        }