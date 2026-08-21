# JobFlow API

<p align="center">
  Backend API for automated job discovery, tracking, email notifications, and data export.
</p>

<p align="center">
  <img src="assets/architecture.png" alt="JobFlow Architecture" width="100%">
</p>



## Overview

JobFlow API is a FastAPI-based backend application that aggregates job listings from multiple sources, stores them in PostgreSQL, and provides authenticated users with tools to search, save, organize, and export jobs.

The application includes a complete authentication system with email verification, background workers for automated scraping and notifications, database migrations using Alembic, and an admin module for maintenance tasks.

The project focuses on building a modular backend architecture by separating routing, business logic, database operations, background workers, and external services into dedicated components.

---

## Features

### Authentication
- User registration and login
- JWT authentication
- Email verification
- Password reset via email
- Password change
- Secure password hashing

### Job Discovery
- Multi-source scraping — **RemoteOK**, **Adzuna**, **Arbeitnow**, **Python.org Jobs**, **Greenhouse**
- Search by title, company, location, source, or keyword
- Sorting by any field (asc/desc)
- Pagination with metadata (page, total, has_next, has_previous)
- Automatic job expiry using `valid_until` and `last_seen` tracking

### User Features
- Save jobs and track application status (saved → applied → interview → rejected)
- Personal dashboard — total jobs, saved, applied, interviews, rejected, added today
- Manage notification keywords
- Personalized job recommendations based on keywords, saved job history, and preferred locations
- Export saved jobs to **PDF** (ReportLab)
- Export saved jobs to **CSV**

### Email Services (via Resend)
- Welcome email
- Email verification OTP
- Password reset OTP
- Job notification digest

### Background Workers
- **Scraper** — runs every 10 minutes, fetches from all 5 sources, deduplicates by link, refreshes `last_seen` on existing jobs
- **Notification worker** — runs every 2 hours, matches new jobs against user keywords, sends digest email, marks jobs as processed
- **Cleanup** — runs daily, deletes expired unsaved jobs, marks expired saved jobs inactive, removes unverified accounts

### Admin
- View users info.
- Manual scrape trigger
- Manual cleanup trigger
- System stats (total/active/inactive jobs, total/verified users, saved jobs, keywords, sources)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.13 |
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Migrations | Alembic |
| Authentication | JWT (PyJWT) + Argon2 |
| Email | Resend |
| Scraping | Requests + BeautifulSoup |
| PDF Reports | ReportLab |
| Testing | Pytest + FastAPI TestClient |
| Server | Uvicorn |

---

## Project Structure

```text

├── src/
│   │
│   ├── main.py
│   │   └── FastAPI application entry point.
│   │       Initializes the application and manages the lifespan/background workers.
│   │
│   ├── database.py
│   │   └── PostgreSQL engine, session factory, and database dependency.
│   │
│   ├── models.py
│   │   └── SQLAlchemy ORM models:
│   │       User, Jobs, SavedJobs, Keywords.
│   │
│   ├── enums.py
│   │   └── Status, SortField, SortOrder enums.
│   │      
│   │
│   ├── admin/
│   │   ├── router.py
│   │   │   └── Admin-only API endpoints.
│   │   ├── schemas.py
│   │   │   └── Admin request/response schemas.
│   │   └── service.py
│   │       └── Administrative business logic.
│   │
│   ├── auth/
│   │   ├── router.py
│   │   │   └── Registration, login, verification,
│   │   │       password reset/change, and account deletion endpoints.
│   │   ├── schemas.py
│   │   │   └── Authentication request/response schemas.
│   │   └── service.py
│   │       └── Authentication business logic.
│   │
│   ├── home/
│   │   ├── router.py
│   │   │   └── Public application/home endpoint.
│   │   └── schemas.py
│   │       └── Home response schemas.
│   │
│   ├── jobs/
│   │   ├── router.py
│   │   │   └── Job browsing and retrieval endpoints.
│   │   ├── schemas.py
│   │   │   └── Job response schemas.
│   │   └── service.py
│   │       └── Job querying, filtering, sorting, and pagination logic.
│   │
│   ├── user/
│   │   ├── router.py
│   │   │   └── Saved jobs, dashboard, keywords, preferences,
│   │   │       exports, recommendations, and profile endpoints.
│   │   ├── schemas.py
│   │   │   └── User-related request/response schemas.
│   │   └── service.py
│   │       └── User business logic and saved-job management.
│   │
│   ├── scraper/
│   │   ├── manager.py
│   │   │   └── Orchestrates all job sources and coordinates
│   │   │       scraping, upserting, and cleanup.
│   │   ├── schemas.py
│   │   │   └── Common scraper response models.
│   │   ├── utils.py
│   │   │   └── Shared scraper utilities, job normalization,
│   │   │       and cleanup-state handling.
│   │   │
│   │   └── sources/
│   │       ├── adzuna.py
│   │       ├── arbeitnow.py
│   │       ├── greenhouse.py
│   │       ├── python_jobs.py
│   │       └── remoteOK.py
│   │           └── Individual job-source integrations.
│   │
│   ├── security/
│   │   ├── jwt_handler.py
│   │   │   └── JWT creation, decoding, and authenticated-user dependencies.
│   │   └── password.py
│   │       └── Password hashing/verification and security utilities.
│   │
│   └── services/
│       ├── cleanup_service.py
│       │   └── Removes expired jobs and performs account/job cleanup.
│       ├── email_service.py
│       │   └── Transactional email delivery through Resend.
│       ├── export_service.py
│       │   └── Generates PDF and CSV exports.
│       ├── job_insert_update.py
│       │   └── Inserts new scraped jobs and updates existing jobs.
│       ├── notification_service.py
│       │   └── Matches jobs against user notification preferences.
│       ├── notification_worker.py
│       │   └── Background worker responsible for notification processing.
│       └── recommendation_service.py
│           └── Generates personalized job recommendations.
│
├── tests/
│   ├── conftest.py
│   │   └── Pytest fixtures, test client, database isolation,
│   │       and FastAPI dependency overrides.
│   ├── db.py
│   │   └── Test PostgreSQL database configuration.
│   ├── test_auth.py
│   │   └── Authentication and authorization tests.
│   ├── test_home.py
│   │   └── Home endpoint tests.
│   ├── test_jobs.py
│   │   └── Job retrieval, filtering, pagination, and lookup tests.
│   └── test_user.py
│       └── Saved jobs, user operations, authorization, and PATCH tests.
│
├── alembic/
│   └── versions/
│       └── Database migration history.
│
├── assets/
│   └── Screenshots and architecture diagrams used by the README.
│
├── config.json
│   └── Scraper configuration such as keywords, countries, and intervals.
│
├── cleanup_state.json
│   └── Persists the last cleanup execution timestamp.
│
├── .env.example
│   └── Example environment variables required to run the application.
│
├── requirements.txt
│   └── Python dependencies.
│
└── README.md
    └── Project documentation.
```

---

## API Endpoints

### Authentication — `/auth`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and get JWT token |
| `PATCH` | `/auth/password_change` | Change password |
| `POST` | `/auth/verify_email` | Send email verification OTP |
| `POST` | `/auth/verify_email/confirm` | Confirm OTP and verify account |
| `POST` | `/auth/forgot_password` | Send password reset OTP |
| `POST` | `/auth/reset_password` | Reset password with OTP |
| `DELETE` | `/auth/delete_account` | Delete account  |

### Jobs — `/jobs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/jobs/` | Browse jobs with filters, sorting, and pagination |
| `GET` | `/jobs/{job_id}` | Get job by ID |

**Query parameters for `GET /jobs/`:**
- `title`, `company`, `location`, `source` — field-level filters
- `keyword` — searches across title, company, location, source
- `sort_by` — any job field
- `sort_order` — `asc` or `desc`
- `page`, `limit` — pagination (default: page 1, limit 20, max 100)

### Users — `/user`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/user/me` | Get current user profile |
| `GET` | `/user/dashboard` | Personal dashboard stats |
| `PATCH` | `/user/me/preferences` | Update notification preferences |
| `POST` | `/user/save/{job_id}` | Save a job |
| `GET` | `/user/` | Get all saved jobs |
| `GET` | `/user/{job_id}` | Get saved job by ID |
| `PATCH` | `/user/edit/{id}` | Update saved job status or notes |
| `DELETE` | `/user/remove/{id}` | Remove a saved job |
| `POST` | `/user/keywords` | Add a notification keyword |
| `GET` | `/user/keywords` | Get all keywords |
| `DELETE` | `/user/delete{id}` | Delete a keyword |
| `GET` | `/user/export_pdf` | Export saved jobs as PDF |
| `GET` | `/user/export_csv` | Export saved jobs as CSV |
| `GET` | `/user/recommended` | Get personalized job recommendations |

### Admin — `/admin`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/get_users` | View users info. |
| `GET` | `/admin/stats` | System-wide stats |
| `POST` | `/admin/scrape` | Manually trigger a scrape |
| `POST` | `/admin/cleanup` | Manually trigger cleanup |

---

## Screenshots

### Swagger UI
![Swagger](assets/swagger.png)

### Authentication
![Authentication](assets/authentication.png)

### Jobs API
![Jobs](assets/jobs.png)

### User Endpoints
![Users](assets/users.png)

### Admin Endpoints
![Admin](assets/admin.png)

### Email Notification
![Notification](assets/notification.png)

### PDF Export
![PDF](assets/pdf.png)

### CSV Export
![CSV](assets/csv.png)

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/qw3rty-dev/jobflow-api.git
cd jobflow-api
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Create your `.env` file**
```bash
cp .env.example .env
```

Fill in your values:
```
APPLICATION_ID=your_adzuna_application_id
APPLICATION_KEY=your_adzuna_application_key
DATABASE_URL=postgresql://username:password@localhost:5432/jobflow_db
SECRET_KEY=your_super_secret_key
RESEND_API_KEY=re_your_resend_api_key
FROM_EMAIL=noreply@yourdomain.com
```

**4. Run database migrations**
```bash
alembic upgrade head
```

**5. Start the server**
```bash
uvicorn src.main:app --reload
```

Background workers (scraper, notification worker, cleanup) start automatically with the server via FastAPI's lifespan.

Open `http://127.0.0.1:8000/docs` for interactive API docs.

---

## Configuration

`config.json` controls scraper behavior without touching code:

```json
{
    "adzuna_keywords": ["backend", "frontend", "intern", "junior", ...],
    "countries": ["gb", "us", "in", "ca", "au", "de"],
    "results_per_page": 20,
    "notification_interval": 7200,
    "scraper_interval": 600,
    "greenhouse_companies": ["discord","reddit",...]
}
```

- `scraper_interval` — how often jobs are fetched (seconds, default 600 = 10 min)
- `notification_interval` — how often notification emails are sent (seconds, default 7200 = 2 hrs)

---

## Testing

JobFlow uses `pytest` for automated testing.

The test suite uses a dedicated PostgreSQL database and FastAPI dependency overrides to keep tests isolated from the development database.

Run the full test suite:

```bash
python -m pytest -v
```


## Future Improvements

- Docker support for simplified deployment
- Redis caching for frequently queried data
- Celery or RQ for robust background task queuing
- OAuth login with Google and GitHub
- Additional job sources (Wellfound, Lever)
- Score-based ranking improvements using more signals (salary, seniority, remote preference) 
- Job analytics dashboard with application insights

---

