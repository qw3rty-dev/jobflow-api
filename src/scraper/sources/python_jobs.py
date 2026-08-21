from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

from src.scraper.schemas import ScraperResponse,Job
from datetime import datetime,timezone


def fetch_python_jobs() -> ScraperResponse:

    headers = {"User-Agent": "Mozilla/5.0" }
    url = "https://www.python.org/jobs/"
    session = requests.Session()
    req = session.get(url,headers = headers)
    if req.status_code != 200:
        print("Request failed")
    else:
        scraped_jobs = []
        seen_links = set()
        soup = BeautifulSoup(req.text,"lxml")
        jobs = soup.select(".list-recent-jobs li")
        for job in jobs:
            tag = job.select_one(".listing-company a")
            if not tag:
                continue
            job_url = tag.get("href")
            if "/jobs/" in job_url:
                job_url = urljoin(url,job_url)
            else:
                continue
            
            if not job_url or job_url in seen_links:
                continue
            sub_req = session.get(job_url) 

            if sub_req.status_code != 200:
                print("Request failed")
                continue
      
            sub_soup = BeautifulSoup(sub_req.text,"lxml")

            company_tag = sub_soup.select_one(".company-name")

            if company_tag:
                data = list(company_tag.stripped_strings)
                job_title = data[0]
                company_name = data[-1]
            else:
                job_title = "N/A"
                company_name = "N/A"
            location_tag = sub_soup.select_one(".listing-location")
            location = location_tag.text.strip() if location_tag else "Unknown"
            date_tag= sub_soup.select_one(".listing-posted time")["datetime"]
            posted_at= datetime.fromisoformat(date_tag).astimezone(timezone.utc) if date_tag else None



            seen_links.add(job_url)

            scraped_jobs.append(
                Job(
            title= job_title,
            company= company_name,
            location= location,
            posted_at =posted_at,
            link= job_url,
            source= "python.org"
            ))
            
        return ScraperResponse(jobs=scraped_jobs)
                
         




