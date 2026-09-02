import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone

from src.scraper.utils import is_valid_url
from src.scraper.schemas import ScraperResponse,Job

def get_job_title(text):
    for sep in (" is hiring", " - hiring", " | hiring", " (hiring", "Is hiring", "Is Hiring"):
     if sep in text:
      text = text.split(sep)[-1].strip()
    noise = ("a","for","-","–","in")
    for word in noise:
        if word in text:
          text=text.strip(word)
    if text == "":
       return None
    return text.strip()




def get_company_title(text):
    for sep in (" is hiring", " - hiring", " | hiring", " (hiring", "Is hiring", "Is Hiring"):
     if sep in text:
      text = text.split(sep)[0].strip()
    if "(YC" in text:
       text = text.split("(YC")[0].strip()
    if text == "":
       return None
    return text.strip()



def fetch_hackernews_jobs():

    URL = "https://news.ycombinator.com/jobs"
    headers = {"User-Agent": "Mozilla/5.0" }
    session = requests.Session()
    req = session.get(URL)
    with requests.Session() as session:
       response = session.get(URL, headers=headers)
    response.raise_for_status()


    soup = BeautifulSoup(req.text,"lxml")

    hn_jobs = soup.select(".athing")
    scraped_jobs = []
    seen_links= set()
    for job in hn_jobs:
        titleline= job.select_one(".titleline a")
        job_url= titleline.get("href")
        if not job_url or job_url in seen_links:
            continue
        if job_url.startswith("item?"):
           job_url = urljoin(URL,job_url)
        if not is_valid_url(job_url):
           continue

        job_title = get_job_title(titleline.text)
        company_name = get_company_title(titleline.text)
        subtext=job.find_next_sibling("tr")   
        posted_at= subtext.select_one(".age").get("title")
        posted_at= posted_at.split()[0]
        posted_at= datetime.fromisoformat(posted_at).replace(tzinfo=timezone.utc)
        if job_title is None or company_name is None or job_url is None :
           continue

        seen_links.add(job_url)

        scraped_jobs.append(
                Job(
            title= job_title,
            company= company_name,
            location= "Unknown",
            posted_at =posted_at,
            link= job_url,
            source= "hackernews"
            ))        
    return ScraperResponse(jobs=scraped_jobs)




