import json
from pathlib import Path
from datetime import datetime,UTC

from src.scraper.schemas import Job

def normalize_location(location: str | None) -> str:
    if not location:
        return "Unknown"
    location= location.strip()
    if "Ø" in location or "Ù" in location:
        try:
            location = location.encode("latin1").decode("utf-8")
        except UnicodeError:
            pass
    return location


def normalize_job(job:Job)-> Job:

    return Job(title = job.title.strip(),
               company = job.company.strip(),
               location = normalize_location(job.location),
               posted_at = job.posted_at,
               link = job.link.strip(),
               source= job.source.strip()
            )

def last_clean_up():
    try:
        PROJECT_ROOT = Path(__file__).resolve().parents[2]
        CONFIG_PATH = PROJECT_ROOT / "cleanup_state.json"
        with open(CONFIG_PATH, "r") as f:
            cleanup = json.load(f)
        print("config", CONFIG_PATH)
        return datetime.fromisoformat(cleanup["last_cleanup_at"])
    except FileNotFoundError:
        return datetime.min.replace(tzinfo= UTC)


def save_last_cleanup():
    cleanup = {"last_cleanup_at" :datetime.now(UTC).isoformat()}
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    CONFIG_PATH = PROJECT_ROOT / "clean_up_state.json"
    with open(CONFIG_PATH, "w") as f:
       json.dump(cleanup,f,indent=4)   