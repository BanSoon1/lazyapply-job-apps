"""
Resume skill extraction — scans uploaded PDF for known tech/soft skills.
"""
import json
import re

SKILL_KEYWORDS = [
    # Programming languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
    "PHP", "Ruby", "Swift", "Kotlin", "R", "MATLAB", "Scala", "Perl",
    # Web / Frontend
    "React", "Vue", "Angular", "HTML", "CSS", "Next.js", "Nuxt", "Tailwind",
    "Bootstrap", "jQuery", "Webpack", "Vite", "REST", "GraphQL",
    # Backend / Frameworks
    "Node.js", "Flask", "Django", "FastAPI", "Spring", "Express", "Laravel",
    "Rails", "ASP.NET",
    # Databases
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle",
    "Elasticsearch", "DynamoDB", "Cassandra",
    # Cloud / DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Terraform",
    "Ansible", "Jenkins", "GitHub Actions", "Linux", "Bash",
    # Data / AI
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas",
    "NumPy", "Scikit-learn", "Data Analysis", "Power BI", "Tableau",
    "Excel", "Statistics",
    # Tools / Practices
    "Git", "Agile", "Scrum", "Jira", "Figma", "Postman", "System Design",
    # Soft skills
    "Communication", "Leadership", "Project Management", "Problem Solving",
]


def extract_text_from_pdf(file_path: str) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages)
    except Exception as e:
        print(f"[ResumeService] PDF parse error: {e}")
        return ""


def extract_skills(file_path: str) -> list[str]:
    text = extract_text_from_pdf(file_path)
    if not text:
        return []

    text_lower = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        # Match whole word only (e.g. "R" shouldn't match "React")
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)

    return found


def process_resume(resume) -> None:
    """Extract skills from resume file and save to DB."""
    from app.extensions import db
    skills = extract_skills(resume.file_path)
    resume.extracted_skills = json.dumps(skills)
    db.session.commit()
    print(f"[ResumeService] Extracted {len(skills)} skills: {skills}")
