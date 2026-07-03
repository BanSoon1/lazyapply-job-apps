"""
Adzuna API — free tier: 100 requests/day.
Register at https://developer.adzuna.com to get APP_ID and APP_KEY.
Fetches from both Malaysia (my) and Singapore (sg).
"""
import requests

BASE = "https://api.adzuna.com/v1/api/jobs"

COUNTRIES = [
    ("sg", "Singapore",  "SGD", "badge-blue"),
    ("gb", "United Kingdom", "£", "badge-orange"),
]


def fetch(app_id, app_key, query="", filters=None):
    filters = filters or {}
    if not app_id or not app_key:
        return []

    all_jobs = []
    for country_code, country_name, currency, badge in COUNTRIES:
        jobs = _fetch_country(app_id, app_key, query, filters,
                              country_code, country_name, currency, badge)
        all_jobs.extend(jobs)

    return all_jobs


def _fetch_country(app_id, app_key, query, filters,
                   country_code, country_name, currency, badge):
    params = {
        "app_id":           app_id,
        "app_key":          app_key,
        "results_per_page": 20,
        "content-type":     "application/json",
        "what":             query or "",
        "sort_by":          "date",
    }

    if filters.get("location"):
        params["where"] = filters["location"]
    if filters.get("salaryMin"):
        params["salary_min"] = filters["salaryMin"]
    if filters.get("jobType"):
        type_map = {"Full-time": "permanent", "Part-time": "part_time",
                    "Contract": "contract", "Internship": "internship"}
        params["contract_time"] = type_map.get(filters["jobType"], "")

    try:
        resp = requests.get(
            f"{BASE}/{country_code}/search/1",
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[Adzuna/{country_code}] fetch error: {e}")
        return []

    jobs = []
    for j in data.get("results", []):
        salary_min = j.get("salary_min") or 0
        salary_max = j.get("salary_max") or 0
        if salary_min and salary_max:
            salary_str = f"{currency} {int(salary_min):,} – {currency} {int(salary_max):,} / month"
        else:
            salary_str = "Salary not disclosed"

        loc     = j.get("location", {}).get("display_name", country_name)
        cat     = j.get("category", {}).get("label", "")
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
            "platformBadge": badge,
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
