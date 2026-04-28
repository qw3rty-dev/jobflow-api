# Job Tracker API 

A backend system that fetches jobs, stores them, filters relevant ones, and send alerts via Telegram.

---

## What it does

- Fetches jobs from external API
- Stores them in a SQLite database 
- Background job fetching (runs continuously)
- Avoid duplicates using job links
- Filters jobs based on keywords
- Send alerts on Telegram when new jobs are found

---

## How It Works

1. The scraper fetches jobs from an external API
2. New jobs are identified by comparing with stored data
3. Jobs are filtered based on keywords
4. Relevant jobs are sent as Telegram alerts
5. Background task runs this process at regular intervals

---

## 🛠 Tech Stack

- FastAPI
- SQLite (sqlite3)
- BeautifulSoup
- Requests
- Python-dotenv

---

## Project Structure

```
job-tracker-api/
│
├── main.py
├── db.py
├── scraper.py
│
├── routes/
│     └── jobs.py
│
├── services/
│     └── alerts.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd job-tracker-api
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Create environment variables**

Create a `.env` file in the root directory:
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

Some useful endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/jobs` | Fetch stored jobs |
| `POST` | `/jobs/scrape` | Manually trigger scraping |
| `GET` | `/jobs/stats` | Get job statistics |

Full API docs are available at `/docs`.

---



---

## Notes

- `.env` is not included for security reasons
- Database (`jobs.db`) is created automatically on first run
- Make sure to start your Telegram bot before using alerts

---

## Future Improvements

- Better filtering logic
- User-specific preferences
- Web dashboard (frontend)
- Support for multiple users

---

