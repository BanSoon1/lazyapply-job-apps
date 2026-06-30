from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models.user import User


def register_user(name: str, email: str, password: str):
    if User.query.filter_by(email=email).first():
        return {"error": "Email already registered"}, 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(name=name, email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.user_id))
    return {"message": "Registration successful", "token": token, "user": user.to_dict()}, 201


def login_user(email: str, password: str):
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return {"error": "Invalid email or password"}, 401

    token = create_access_token(identity=str(user.user_id))
    return {"message": "Login successful", "token": token, "user": user.to_dict()}, 200


def update_profile(user_id: int, data: dict):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    allowed_fields = ("name", "preferred_location", "preferred_job_type")
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()
    return {"message": "Profile updated", "user": user.to_dict()}, 200