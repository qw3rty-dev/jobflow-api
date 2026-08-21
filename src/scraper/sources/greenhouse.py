import json
import requests
from pathlib import Path
from src.scraper.schemas import ScraperResponse,Job


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = PROJECT_ROOT / "config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)
COMPANIES = config["greenhouse_companies"]


def fetch_greenhouse_jobs():

    jobs= []
    seen_links= set()
    headers = {"User-Agent": "Mozilla/5.0" }

    for company in COMPANIES:
        URL= f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
        with requests.Session() as session:
            response = session.get(URL,headers=headers)
        response.raise_for_status

        data= response.json()
        for job in data["jobs"]:

            job_url = job.get("absolute_url","N/A").strip()
            if not job_url or job_url in seen_links:
                continue
            seen_links.add(job_url)

            jobs.append(
                            Job(
                        title= job.get("title","N/A").strip(),
                        company= job.get("company_name", "N/A").strip(),
                        location= job.get("location").get("name").strip() or "Unknown",
                        posted_at= job.get("first_published","N/A").strip(),
                        link= job_url,
                        source= "greenhouse"
                        ))
                
    return ScraperResponse(jobs=jobs)
            


        

