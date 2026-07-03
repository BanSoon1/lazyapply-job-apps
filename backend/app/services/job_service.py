import os
import time
import threading

from app.extensions import db
from app.models.job import Job

_cache: dict = {}
_cache_lock = threading.Lock()
CACHE_TTL = 300  # seconds


def _cache_get(key):
    with _cache_lock:
        entry = _cache.get(key)
        if entry and (time.time() - entry[0]) < CACHE_TTL:
            return entry[1]
    return None


def _cache_set(key, data):
    with _cache_lock:
        _cache[key] = (time.time(), data)


def search_jobs(query: str, location: str = "", job_type: str = "", sal_min: str = "") -> dict:
    filters = {k: v for k, v in {
        "location":  location,
        "jobType":   job_type,
        "salaryMin": sal_min,
    }.items() if v}

    cache_key = f"{query}|{location}|{job_type}|{sal_min}"
    cached = _cache_get(cache_key)
    if cached:
        return {"jobs": cached, "count": len(cached), "source": "cache", "errors": []}

    raw_jobs, errors, sources_used = [], [], []

    # RemoteOK
    try:
        from scrapers import remoteok
        rok = remoteok.fetch(query, filters)
        raw_jobs.extend(rok)
        sources_used.append("RemoteOK")
    except Exception as e:
        errors.append(f"RemoteOK: {e}")

    # The Muse
    try:
        from scrapers import themuse
        muse = themuse.fetch(query, filters)
        raw_jobs.extend(muse)
        sources_used.append("The Muse")
    except Exception as e:
        errors.append(f"TheMuse: {e}")

    # JSearch
    rapidapi_key = os.getenv("RAPIDAPI_KEY", "").strip()
    if rapidapi_key:
        try:
            from scrapers import jsearch
            js = jsearch.fetch(rapidapi_key, query, filters)
            raw_jobs.extend(js)
            sources_used.append("JSearch")
        except Exception as e:
            errors.append(f"JSearch: {e}")

    # Adzuna
    az_id  = os.getenv("ADZUNA_APP_ID",  "").strip()
    az_key = os.getenv("ADZUNA_APP_KEY", "").strip()
    if az_id and az_key:
        try:
            from scrapers import adzuna
            az = adzuna.fetch(az_id, az_key, query, filters)
            raw_jobs.extend(az)
            sources_used.append("Adzuna")
        except Exception as e:
            errors.append(f"Adzuna: {e}")

    # Deduplicate by title + company
    seen: set = set()
    unique_raw = []
    for j in raw_jobs:
        key = (j["title"].lower().strip(), j["company"].lower().strip())
        if key not in seen:
            seen.add(key)
            unique_raw.append(j)

    unique_raw.sort(key=lambda j: (_region_priority(j), _recency_sort_key(j)))

    # Upsert into DB and return DB records
    result = []
    for j in unique_raw:
        job = _upsert_job(j)
        result.append(job.to_dict())

    _cache_set(cache_key, result)

    return {"jobs": result, "count": len(result), "sources": sources_used, "errors": errors}


def _upsert_job(data: dict) -> Job:
    """Insert job if not exists, otherwise return existing record."""
    existing = Job.query.filter_by(
        title=data.get("title", ""),
        company=data.get("company", ""),
    ).first()

    if existing:
        return existing

    job = Job(
        title=data.get("title", ""),
        company=data.get("company", ""),
        location=data.get("location", ""),
        salary=data.get("salary", ""),
        job_type=data.get("jobType", ""),
        description=data.get("description", ""),
        source_platform=data.get("source", ""),
        source_url=data.get("applyUrl", ""),
        posted_label=data.get("postedLabel", ""),
    )
    db.session.add(job)
    db.session.commit()
    return job


def _recency_sort_key(j):
    label = j.get("postedLabel", "")
    if label == "Today":     return 0
    if label == "1 day ago": return 1
    if "days ago" in label:
        try:
            return int(label.split()[0])
        except ValueError:
            pass
    return 99

def _region_priority(j):
    location = (j.get("location") or "").lower()
    if any(k in location for k in ["singapore", "malaysia", "kuala lumpur", "johor", "penang"]):
        return 0
    return 1  