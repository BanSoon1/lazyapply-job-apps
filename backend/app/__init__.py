import os
from flask import Flask
from flask_cors import CORS

from app.config.settings import get_config
from app.extensions import db, jwt, bcrypt


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]
    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    if frontend_url:
        allowed_origins.append(frontend_url)

    CORS(app, origins=allowed_origins)
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.jobs import jobs_bp
    from app.routes.saved_jobs import saved_jobs_bp
    from app.routes.resume import resume_bp
    from app.routes.recommendations import recommendations_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(saved_jobs_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(recommendations_bp)

    with app.app_context():
        from app.models import user, job, resume, saved_job  # noqa: F401
        db.create_all()

    return app