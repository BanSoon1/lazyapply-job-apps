# LazyApply — Job Aggregator

A full-stack job aggregation platform built with Flask (backend) and vanilla JS (frontend). Aggregates real job listings from multiple sources and provides AI-powered match scoring based on your profile.

## Features

- **Multi-source job search** — RemoteOK, The Muse, Adzuna (Malaysia + Singapore)
- **AI Match scoring** — scores each job based on your preferred location, job type, and resume skills
- **Save jobs** — bookmark jobs to your account
- **Resume upload** — store your resume on your profile
- **Dark mode** — persisted across sessions
- **JWT authentication** — secure register/login

## Project Structure

```
lazyapply_completed/
├── backend/
│   ├── app/
│   │   ├── config/        # App configuration
│   │   ├── models/        # SQLAlchemy models (User, Job, Resume, SavedJob)
│   │   ├── routes/        # Flask Blueprints (auth, jobs, saved_jobs, resume, recommendations)
│   │   └── services/      # Business logic (auth, jobs, recommendations)
│   ├── scrapers/          # Job source scrapers (RemoteOK, The Muse, Adzuna, JSearch)
│   ├── uploads/           # Uploaded resumes
│   ├── .env               # Environment variables (not committed)
│   ├── requirements.txt
│   └── run.py             # Entry point
└── frontend/
    └── index.html         # Single-page app
```

## Setup

### Prerequisites

- Python 3.10+
- A free [Adzuna API key](https://developer.adzuna.com) (for Malaysia/Singapore jobs)

### 1. Clone the repo

```bash
git clone https://github.com/BanSoon1/lazyapply-job-app.git
cd lazyapply-job-app
```

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
```

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///lazyapply.db
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
```

Start the backend:

```bash
python run.py
```

Backend runs at **http://127.0.0.1:5000**

### 3. Serve the frontend

Open a new terminal:

```bash
cd frontend
python -m http.server 3000
```

Open **http://127.0.0.1:3000** in your browser.

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/register` | — | Register new user |
| POST | `/api/login` | — | Login and get JWT token |
| GET/PUT | `/api/profile` | JWT | Get or update user profile |
| GET | `/api/jobs/search?q=&location=&jobType=` | — | Search jobs |
| GET | `/api/jobs/<id>` | — | Get single job |
| GET/POST | `/api/saved-jobs/` | JWT | List or save a job |
| DELETE | `/api/saved-jobs/<id>` | JWT | Remove a saved job |
| GET/POST | `/api/resume/` | JWT | Get or upload resume |
| GET | `/api/recommendations` | JWT | Get AI-matched job recommendations |

## Job Sources

| Source | Region | API Key Required |
|--------|--------|-----------------|
| RemoteOK | Global (Remote) | No |
| The Muse | Global | No |
| Adzuna | Malaysia + Singapore | Yes (free) |
| JSearch | Global (Indeed/LinkedIn data) | Yes (RapidAPI free tier) |

## AI Match Scoring

Each job is scored based on your profile preferences:

- **+40 points** — job location matches your preferred location
- **+30 points** — job type matches your preferred job type  
- **+10 points** — each resume skill found in the job description

Set your preferences in **Profile → Job Preferences** to activate scoring.

## Tech Stack

- **Backend**: Python, Flask, SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt
- **Database**: SQLite
- **Frontend**: Vanilla JS, HTML, CSS (single-page app)
- **Job Sources**: RemoteOK API, The Muse API, Adzuna API
