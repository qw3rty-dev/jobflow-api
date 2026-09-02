from datetime import datetime

import requests

from src.scraper.utils import is_valid_url
from src.scraper.schemas import Job,ScraperResponse

def fetch_remoteok_jobs()-> ScraperResponse: 
    
    """Fetch jobs from RemoteOK and return a list of unique job dicts."""
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "Mozilla/5.0"}

    with requests.Session() as session:
        response = session.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    jobs = []
    seen_links = set()

    for job in data[1:]:
        job_url = job.get("url","N/A").strip()
        if not job_url or job_url in seen_links:
            continue
        if not is_valid_url(job_url):
           continue
        seen_links.add(job_url)
        posted_tag = job.get("date")
        posted_at = datetime.fromisoformat(posted_tag) if posted_tag else None
        jobs.append(
                Job(
            title= job.get("position","N/A").strip(),
            company= job.get("company", "N/A").strip(),
            location= job.get("location").strip() or "Unknown",
            posted_at= posted_at,
            link= job_url,
            source= "remoteOK"
            ))

    return ScraperResponse(jobs=jobs)




    



