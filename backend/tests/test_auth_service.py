"""
Tests for auth_service — register, login, update profile.
Run with: pytest tests/
"""
import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def ctx(app):
    with app.app_context():
        yield


# ── Register ────────────────────────────────────────────────────────────────

def test_register_success(ctx):
    from app.services.auth_service import register_user
    data, status = register_user("Alice", "alice@example.com", "password123")
    assert status == 201
    assert "token" in data
    assert data["user"]["email"] == "alice@example.com"


def test_register_duplicate_email(ctx):
    from app.services.auth_service import register_user
    register_user("Alice", "alice@example.com", "password123")
    data, status = register_user("Alice2", "alice@example.com", "password456")
    assert status == 409
    assert "error" in data


# ── Login ────────────────────────────────────────────────────────────────────

def test_login_success(ctx):
    from app.services.auth_service import register_user, login_user
    register_user("Bob", "bob@example.com", "secret")
    data, status = login_user("bob@example.com", "secret")
    assert status == 200
    assert "token" in data


def test_login_wrong_password(ctx):
    from app.services.auth_service import register_user, login_user
    register_user("Bob", "bob@example.com", "secret")
    data, status = login_user("bob@example.com", "wrongpassword")
    assert status == 401
    assert "error" in data


def test_login_unknown_email(ctx):
    from app.services.auth_service import login_user
    data, status = login_user("nobody@example.com", "secret")
    assert status == 401


# ── Update Profile ───────────────────────────────────────────────────────────

def test_update_profile(ctx):
    from app.services.auth_service import register_user, update_profile
    reg_data, _ = register_user("Carol", "carol@example.com", "pass")
    user_id = reg_data["user"]["user_id"]
    data, status = update_profile(user_id, {"preferred_location": "Kuala Lumpur"})
    assert status == 200
    assert data["user"]["preferred_location"] == "Kuala Lumpur"
