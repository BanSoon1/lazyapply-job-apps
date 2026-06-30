"""
JSearch via RapidAPI — aggregates LinkedIn, Indeed, Glassdoor, ZipRecruiter.
Free tier: 200 requests/month.
Sign up: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
"""
import requests

BASE = "https://jsearch.p.rapidapi.com/search"

PLATFORM_BADGE = {
    "linkedin":    "badge-blue",
    "indeed":      "badge-purple",
    "glassdoor":   "badge-green",
    "ziprecruiter":"badge-red",
    "jobstreet":   "badge-orange",
}

def fetch(api_key, query="", filters=None):
    filters = filters or {}
    if not api_key:
        return []

    params = {
        "query":     (query or "developer") + (" in Malaysia" if not filters.get("location") else f" in {filters['location']}"),
        "page":      "1",
        "num_pages": "2",
        "language":  "en",
    }

    type_map = {
        "Full-time":  "FULLTIME",
        "Part-time":  "PARTTIME",
        "Contract":   "CONTRACTOR",
        "Internship": "INTERN",
    }
    if filters.get("jobType"):
        params["employment_types"] = type_map.get(filters["jobType"], "FULLTIME")

    try:
        resp = requests.get(
            BASE,
            headers={
                "x-rapidapi-key":  api_key,
                "x-rapidapi-host": "jsearch.p.rapidapi.com",
            },
            params=params,
            timeout=12,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[JSearch] fetch error: {e}")
        return []

    jobs = []
    for j in data.get("data", []):
        publisher = j.get("job_publisher", "Indeed")
        pub_key   = publisher.lower() if publisher else "indeed"
        badge     = next((v for k, v in PLATFORM_BADGE.items() if k in pub_key), "badge-gray")

        salary_min = j.get("job_min_salary") or 0
        salary_max = j.get("job_max_salary") or 0
        currency   = j.get("job_salary_currency", "USD")
        period     = j.get("job_salary_period", "YEAR")
        salary_str = (
            f"{currency} {int(salary_min):,} – {int(salary_max):,} / {period.lower()}"
            if salary_min and salary_max else "Salary not disclosed"
        )

        location_parts = [j.get("job_city"), j.get("job_state"), j.get("job_country")]
        location = ", ".join(p for p in location_parts if p) or "Not specified"

        emp_type_raw = j.get("job_employment_type", "FULLTIME")
        emp_type_map = {"FULLTIME":"Full-time","PARTTIME":"Part-time","CONTRACTOR":"Contract","INTERN":"Internship"}
        emp_type = emp_type_map.get(emp_type_raw, "Full-time")

        # Salary filter
        if filters.get("salaryMin") and salary_max:
            if salary_max < int(filters["salaryMin"]):
                continue

        highlights = j.get("job_highlights") or {}
        jobs.append({
            "id":           f"jsearch_{j['job_id']}",
            "title":        j.get("job_title", ""),
            "company":      j.get("employer_name", "Unknown"),
            "location":     location,
            "jobType":      emp_type,
            "salary":       salary_str,
            "salaryMin":    salary_min,
            "salaryMax":    salary_max,
            "source":       publisher,
            "platformBadge":badge,
            "applyUrl":     j.get("job_apply_link") or j.get("job_google_link", "#"),
            "postedLabel":  _days_ago(j.get("job_posted_at_datetime_utc", "")),
            "logo":         j.get("employer_logo") or _avatar(j.get("employer_name", "?"), "3b82f6"),
            "description":  j.get("job_description", ""),
            "requirements": highlights.get("Qualifications", [])[:8],
            "benefits":     highlights.get("Benefits", [])[:6],
        })

    return jobs


def _days_ago(date_str):
    if not date_str:
        return "Recently"
    from datetime import datetime, timezone
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        diff = (datetime.now(timezone.utc) - dt).days
        if diff == 0:  return "Today"
        if diff == 1:  return "1 day ago"
        return f"{diff} days ago"
    except Exception:
        return "Recently"


def _avatar(name, color="3b82f6"):
    return f"https://ui-avatars.com/api/?name={requests.utils.quote(name)}&background={color}&color=fff&size=64&bold=true"
