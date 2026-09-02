from datetime import datetime,UTC

import requests

from src.scraper.utils import is_valid_url
from src.scraper.schemas import ScraperResponse,Job

def fetch_arbeitnow_jobs()-> ScraperResponse:

    url="https://www.arbeitnow.com/api/job-board-api"
    headers = {"User-Agent": "Mozilla/5.0" }

    with requests.Session() as session:
        response = session.get(url, headers=headers)
    response.raise_for_status()

    data= response.json()
    jobs= []
    seen_links= set()
    for job in data['data']:
        
        job_url = job.get("url","N/A").strip()
        if not job_url or job_url in seen_links:
            continue
        if not is_valid_url(job_url):
           continue

        seen_links.add(job_url)
        posted_tag= job.get("created_at")
        posted_at = datetime.fromtimestamp(posted_tag,tz=UTC) if posted_tag else None


        jobs.append(
                Job(
            title= job.get("title","N/A").strip(),
            company= job.get("company_name", "N/A").strip(),
            location= job.get("location").strip() or "Unknown",
            posted_at= posted_at,
            link= job_url,
            source= "arbeitnow"
            ))
        
    return ScraperResponse(jobs=jobs)
    
      
    