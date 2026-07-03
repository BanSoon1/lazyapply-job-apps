"""
Tests for job_service — search, deduplication, region priority.
Run with: pytest tests/
"""
import pytest
from unittest.mock import patch
from app import create_app
from app.extensions import db


MOCK_JOBS = [
    {
        "id": "rok_1", "title": "Python Developer", "company": "TechCorp",
        "location": "Kuala Lumpur, Malaysia", "jobType": "Full-time",
        "salary": "RM 5,000 – RM 8,000 / month", "salaryMin": 5000, "salaryMax": 8000,
        "source": "RemoteOK", "platformBadge": "badge-green",
        "applyUrl": "https://remoteok.com/1", "postedLabel": "Today",
        "logo": "", "description": "Python backend role.", "requirements": ["python"],
        "benefits": [],
    },
    {
        "id": "muse_1", "title": "Frontend Engineer", "company": "StartupSG",
        "location": "Singapore", "jobType": "Full-time",
        "salary": "SGD 5,000 – SGD 7,000 / month", "salaryMin": 5000, "salaryMax": 7000,
        "source": "The Muse", "platformBadge": "badge-purple",
        "applyUrl": "https://themuse.com/1", "postedLabel": "2 days ago",
        "logo": "", "description": "React frontend role.", "requirements": ["react"],
        "benefits": [],
    },
    {
        "id": "rok_2", "title": "Data Analyst", "company": "GlobalCo",
        "location": "Remote", "jobType": "Contract",
        "salary": "Salary not disclosed", "salaryMin": 0, "salaryMax": 0,
        "source": "RemoteOK", "platformBadge": "badge-green",
        "applyUrl": "https://remoteok.com/2", "postedLabel": "5 days ago",
        "logo": "", "description": "Data analytics role.", "requirements": ["sql"],
        "benefits": [],
    },
]


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


def test_search_returns_jobs(ctx):
    """search_jobs returns a list of jobs with expected keys."""
    from app.services.job_service import search_jobs
    with patch("scrapers.remoteok.fetch", return_value=MOCK_JOBS[:1]), \
         patch("scrapers.themuse.fetch",  return_value=[]):
        result = search_jobs("python")
    assert result["count"] >= 1
    job = result["jobs"][0]
    assert "title" in job
    assert "company" in job


def test_search_deduplicates(ctx):
    """Duplicate title+company entries are removed."""
    import app.services.job_service as svc
    svc._cache.clear()
    from app.services.job_service import search_jobs
    duplicate = MOCK_JOBS[0].copy()
    duplicate["id"] = "rok_99"
    with patch("scrapers.remoteok.fetch", return_value=[MOCK_JOBS[0], duplicate]), \
         patch("scrapers.themuse.fetch",  return_value=[]), \
         patch("scrapers.adzuna.fetch",   return_value=[]):
        result = search_jobs("python")
    assert result["count"] == 1


def test_region_priority(ctx):
    """Malaysia/Singapore jobs appear before remote jobs."""
    from app.services.job_service import search_jobs
    with patch("scrapers.remoteok.fetch", return_value=MOCK_JOBS), \
         patch("scrapers.themuse.fetch",  return_value=[]):
        result = search_jobs("")
    locations = [j["location"] for j in result["jobs"]]
    remote_idx = next((i for i, l in enumerate(locations) if "Remote" in l), None)
    sg_idx     = next((i for i, l in enumerate(locations) if "Singapore" in l), None)
    if remote_idx is not None and sg_idx is not None:
        assert sg_idx < remote_idx
