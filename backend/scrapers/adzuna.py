"""
Adzuna API — free tier: 100 requests/day.
Register at https://developer.adzuna.com to get APP_ID and APP_KEY.
Covers Malaysia (country code: my), UK, US, AU and more.
"""
import requests

BASE = "https://api.adzuna.com/v1/api/jobs"
COUNTRY = "my"   # Malaysia

def fetch(app_id, app_key, query="", filters=None):
    filters = filters or {}
    if not app_id or not app_key:
        return []

    params = {
        "app_id":          app_id,
        "app_key":         app_key,
        "results_per_page": 20,
        "content-type":    "application/json",
        "what":            query or "developer",
        "sort_by":         "date",
    }

    if filters.get("location"):
        params["where"] = filters["location"]
    if filters.get("salaryMin"):
        params["salary_min"] = filters["salaryMin"]
    if filters.get("jobType"):
        type_map = {"Full-time": "permanent", "Part-time": "part_time",
                    "Contract": "contract", "Internship": "internship"}
        params["full_time"] = type_map.get(filters["jobType"], "")

    try:
        resp = requests.get(
            f"{BASE}/{COUNTRY}/search/1",
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[Adzuna] fetch error: {e}")
        return []

    jobs = []
    for j in data.get("results", []):
        salary_min = j.get("salary_min") or 0
        salary_max = j.get("salary_max") or 0
        salary_str = (
            f"RM {int(salary_min):,} – RM {int(salary_max):,} / month"
            if salary_min and salary_max else "Salary not disclosed"
        )
        loc  = j.get("location", {}).get("display_name", "Malaysia")
        cat  = j.get("category", {}).get("label", "")
        company = j.get("company", {}).get("display_name", "Unknown")

        jobs.append({
            "id":           f"adzuna_{j['id']}",
            "title":        j.get("title", ""),
            "company":      company,
            "location":     loc,
            "jobType":      _map_type(j),
            "salary":       salary_str,
            "salaryMin":    salary_min,
            "salaryMax":    salary_max,
            "source":       "Adzuna",
            "platformBadge":"badge-orange",
            "applyUrl":     j.get("redirect_url", "#"),
            "postedLabel":  _days_ago(j.get("created", "")),
            "logo":         _avatar(company),
            "description":  j.get("description", ""),
            "requirements": [cat] if cat else [],
            "benefits":     [],
        })

    return jobs


def _map_type(j):
    ct = j.get("contract_time", "")
    ct_type = j.get("contract_type", "")
    if "part" in ct.lower():       return "Part-time"
    if "contract" in ct_type.lower(): return "Contract"
    return "Full-time"


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


def _avatar(name):
    return f"https://ui-avatars.com/api/?name={requests.utils.quote(name)}&background=ea580c&color=fff&size=64&bold=true"
