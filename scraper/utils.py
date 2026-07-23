from datetime import datetime,UTC
import json

from schemas import Job

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
        with open("cleanup_state.json", "r") as f:
            cleanup = json.load(f)
        return datetime.fromisoformat(cleanup["last_cleanup_at"])
    except FileNotFoundError:
        return datetime.min.replace(tzinfo= UTC)


def save_last_cleanup():
    cleanup = {"last_cleanup_at" :datetime.now(UTC).isoformat()}
    with open("cleanup_state.json", "w") as f:
      json.dump(cleanup,f,indent=4)   