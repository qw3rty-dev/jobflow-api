# Job Tracker API

A FastAPI-based backend system that automatically fetches remote jobs, filters relevant ones, stores them locally, and sends real-time alerts via Telegram.

---

## Overview

This project automates the job discovery process by integrating scraping, filtering, storage, and notification into a single pipeline.

### Key Features

- Fetches jobs from RemoteOK API
- Stores jobs in SQLite database
- Avoids duplicates using unique job links
- Filters jobs based on predefined keywords
- Sends Telegram alerts for relevant jobs
- Runs automatically in the background every 10 minutes
- Manual scrape trigger via API

---

## How It Works

1. The system fetches jobs from the RemoteOK API
2. Existing job links are checked to prevent duplicates
3. Jobs are filtered using hardcoded keywords
4. Filtered jobs are stored in the database
5. New relevant jobs are sent as a single Telegram message
6. This process runs automatically every 10 minutes using a background thread

---

## Tech Stack

- **FastAPI** – API framework
- **SQLite (sqlite3)** – Lightweight database
- **Requests** – API calls
- **Threading** – Background job execution
- **Python-dotenv** – Environment variable management

---

## Project Structure

```
job-tracker-api/
│
├── main.py              # App entry + background thread
├── database.py          # DB connection + table initialization
├── scraper.py           # Fetch, filter, and process jobs
│
├── routes/
│     └── jobs.py        # All job-related endpoints
│
├── services/
│     └── alerts.py      # Telegram alert logic
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup Instructions

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd job-tracker-api
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Setup environment variables**

Create a `.env` file:
```
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
```

**4. Run the application**
```bash
uvicorn main:app --reload
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/jobs/` | Create a job manually |
| `GET` | `/jobs/` | Get all stored jobs |
| `POST` | `/jobs/scrape` | Trigger manual scraping |
| `GET` | `/jobs/stats` | Get job statistics |
| `GET` | `/jobs/{job_id}` | Get job by ID |
| `DELETE` | `/jobs/{job_id}` | Delete job |
| `PUT` | `/jobs/{job_id}` | Mark job as applied |

 Interactive docs available at: `/docs`

---

## Example Response

```json
{
  "id": 1,
  "title": "Backend Developer",
  "company": "Example Inc",
  "location": "Remote",
  "link": "https://remoteOK.com/remote-jobs/job/123",
  "applied": false
}
```

---

## Stats Endpoint

`GET /jobs/stats` returns:

```json
{
  "total_jobs": 50,
  "applied": 10,
  "pending": 40
}
```

---

## Telegram Alerts

- Sends one combined message per scrape
- Includes only filtered jobs
- Triggered only when new relevant jobs are found

Format:
```
Title at Company
Location: XYZ
https://...
```

---

## Database Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key (auto increment) |
| `title` | Text | Job title |
| `company` | Text | Company name |
| `location` | Text | Job location |
| `link` | Text | Unique job URL |
| `applied` | Boolean | Application status |

---

## Background Processing

- Runs using a threaded loop
- Executes every 10 minutes
- Automatically starts with the application
- Can also be triggered manually via API

---

## Notes

- `.env` file is not included for security reasons
- Database is created automatically on first run
- Ensure your Telegram bot is active before running

---

## Future Improvements

- User-specific job preferences
- Authentication system
- Web dashboard (frontend)
- Multi-user support
- Advanced filtering logic

---

