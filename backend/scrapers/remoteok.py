"""
RemoteOK — free public JSON API, no key needed.
Docs: https://remoteok.com/api
"""
import requests

HEADERS = {"User-Agent": "LazyApply/1.0 (job aggregator)"}

def fetch(query="", filters=None):
    filters = filters or {}
    try:
        resp = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[RemoteOK] fetch error: {e}")
        return []

    jobs = []
    for item in data:
        # First element is a metadata object, skip it
        if not isinstance(item, dict) or "id" not in item:
            continue

        title    = item.get("position", "")
        company  = item.get("company", "Unknown")
        tags     = item.get("tags", [])
        location = item.get("location") or "Remote"
        salary   = _salary(item)

        # Keyword filter
        if query:
            q = query.lower()
            if not (q in title.lower() or q in company.lower()
                    or any(q in t.lower() for t in tags)):
                continue

        # Job-type filter — RemoteOK is always remote/contract
        if filters.get("jobType") and filters["jobType"] not in ("Contract", "Full-time"):
            continue

        jobs.append({
            "id":          f"rok_{item['id']}",
            "title":       title,
            "company":     company,
            "location":    location,
            "jobType":     "Full-time",
            "salary":      salary,
            "salaryMin":   item.get("salary_min") or 0,
            "salaryMax":   item.get("salary_max") or 0,
            "source":      "RemoteOK",
            "platformBadge": "badge-green",
            "applyUrl":    item.get("url") or f"https://remoteok.com/remote-jobs/{item['id']}",
            "postedLabel": _days_ago(item.get("date", "")),
            "logo":        item.get("company_logo") or _avatar(company),
            "description": item.get("description") or f"Remote {title} position at {company}.",
            "requirements": tags[:8],
            "benefits":    ["Remote work", "Flexible hours"],
        })

    # Salary filter
    if filters.get("salaryMin"):
        min_s = int(filters["salaryMin"])
        jobs = [j for j in jobs if j["salaryMax"] == 0 or j["salaryMax"] >= min_s]

    return jobs[:30]


def _salary(item):
    lo, hi = item.get("salary_min"), item.get("salary_max")
    if lo and hi:
        return f"${int(lo):,} – ${int(hi):,} / year"
    if lo:
        return f"${int(lo):,}+ / year"
    return "Salary not disclosed"


def _days_ago(date_str):
    if not date_str:
        return "Recently"
    from datetime import datetime, timezone
    try:
        dt   = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        diff = (datetime.now(timezone.utc) - dt).days
        if diff == 0:  return "Today"
        if diff == 1:  return "1 day ago"
        return f"{diff} days ago"
    except Exception:
        return "Recently"


def _avatar(name):
    return f"https://ui-avatars.com/api/?name={requests.utils.quote(name)}&background=16a34a&color=fff&size=64&bold=true"
