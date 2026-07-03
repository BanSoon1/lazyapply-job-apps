"""
The Muse API — free public API, no key required for basic search.
Docs: https://www.themuse.com/developers/api/v2
"""
import requests

BASE = "https://www.themuse.com/api/public/jobs"
HEADERS = {"User-Agent": "LazyApply/1.0"}

LEVEL_MAP = {
    "Entry Level":  "Entry Level",
    "Mid Level":    "Mid Level",
    "Senior Level": "Senior Level",
    "Management":   "Management",
}

def fetch(query="", filters=None):
    filters = filters or {}
    params = {"page": 1, "descending": "true"}
    if query:
        params["category"] = query  # The Muse uses categories, keyword search is limited

    try:
        resp = requests.get(BASE, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[TheMuse] fetch error: {e}")
        return []

    jobs = []
    for item in data.get("results", []):
        title   = _fix_encoding(item.get("name", ""))
        company = _fix_encoding(item.get("company", {}).get("name", "Unknown"))
        locs    = item.get("locations", [])
        location = locs[0].get("name", "Remote") if locs else "Remote"
        levels  = [l.get("name", "") for l in item.get("levels", [])]
        job_type = _map_type(levels)
        refs    = item.get("refs", {})
        apply_url = refs.get("landing_page", "#")

        # Keyword filter
        if query:
            q = query.lower()
            cats = [c.get("name", "").lower() for c in item.get("categories", [])]
            if not (q in title.lower() or q in company.lower() or any(q in c for c in cats)):
                continue

        # Job type filter
        if filters.get("jobType") and filters["jobType"] != job_type:
            continue

        # Location filter (The Muse is mostly US remote)
        if filters.get("location") and filters["location"].lower() not in location.lower():
            if filters["location"] != "Remote":
                continue

        jobs.append({
            "id":           f"muse_{item['id']}",
            "title":        title,
            "company":      company,
            "location":     location,
            "jobType":      job_type,
            "salary":       "Salary not disclosed",
            "salaryMin":    0,
            "salaryMax":    0,
            "source":       "The Muse",
            "platformBadge":"badge-purple",
            "applyUrl":     apply_url,
            "postedLabel":  _days_ago(item.get("publication_date", "")),
            "logo":         item.get("company", {}).get("refs", {}).get("logo_image") or _avatar(company),
            "description":  _strip_html(item.get("contents", "")),
            "requirements": [l for l in levels if l],
            "benefits":     ["Career growth", "Inclusive culture"],
        })

    return jobs[:30]


def _fix_encoding(text):
    if not text:
        return text
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text


def _map_type(levels):
    for l in levels:
        if "intern" in l.lower():   return "Internship"
        if "senior" in l.lower():   return "Full-time"
        if "entry"  in l.lower():   return "Full-time"
    return "Full-time"


def _strip_html(html):
    if not html:
        return ""
    from html.parser import HTMLParser
    class _P(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []
        def handle_data(self, data):
            self.parts.append(data)
    p = _P()
    p.feed(html)
    return " ".join(p.parts)[:2000]


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
    return f"https://ui-avatars.com/api/?name={requests.utils.quote(name)}&background=7c3aed&color=fff&size=64&bold=true"
