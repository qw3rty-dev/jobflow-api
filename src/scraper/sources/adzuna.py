import os
import json
import asyncio
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

import httpx

from src.scraper.utils import is_valid_url
from src.scraper.schemas import Job,ScraperResponse

load_dotenv()

APPLICATION_ID = os.getenv("APPLICATION_ID")
APPLICATION_KEY = os.getenv("APPLICATION_KEY")
BATCH_SIZE = 10


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = PROJECT_ROOT / "config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

KEYWORDS = config["adzuna_keywords"]

COUNTRIES = config["countries"]

RESULTS_PER_PAGE = config["results_per_page"]

async def fetch_page(client,url,params,country,keyword):
    semaphore = asyncio.Semaphore(5)
    async with semaphore:
        response = await client.get(url,params=params)
        if response.status_code ==429:
            # print(f"429: {country=} {keyword=}")
            return None
    return response.json()


async def fetch_adzuna_jobs() ->ScraperResponse:
    jobs=[]
    seen_links = set()
    async with httpx.AsyncClient() as client:
        tasks =[]
        for country in COUNTRIES:
            for keyword in KEYWORDS:

                URL =  f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

                params = {
                    "app_id": APPLICATION_ID,
                    "app_key": APPLICATION_KEY,
                    "what": keyword,
                    "results_per_page": RESULTS_PER_PAGE,
                    "sort_by": "date"
                }
                tasks.append(fetch_page(client,URL,params,country,keyword))
        
        for i in range(0,len(tasks),BATCH_SIZE):
            batch = tasks[i:i+BATCH_SIZE]
            responses = await asyncio.gather(*batch,return_exceptions=True)    
            await asyncio.sleep(2)

            for data in responses:
                if data is None:
                    continue
                if isinstance(data,Exception):
                    # print(data)
                    continue

                for result in data["results"]:

                    job_url = result.get("redirect_url","N/A").strip().split("?")[0]

                    if not job_url or job_url in seen_links:
                        continue
                    if not is_valid_url(job_url):
                        continue
                    seen_links.add(job_url)

                    title = result.get("title","N/A").strip()
                    company = result.get("company",{}).get("display_name","N/A").strip()
                    location = result.get("location",{}).get("display_name").strip() or "Unknown"
                    posted_tag = result.get("created")
                    posted_at = datetime.strptime(posted_tag,"%Y-%m-%dT%H:%M:%SZ")

                    

                    jobs.append(
                            Job(
                        title= title,
                        company= company,
                        location= location,
                        posted_at= posted_at,
                        link= job_url,
                        source= "adzuna"
                        ))

    return ScraperResponse(jobs=jobs)

