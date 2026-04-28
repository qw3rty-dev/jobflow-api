import requests
from database import get_connection
from services.alerts import send_telegram_alert

KEYWORDS= ["python","intern","developer","remote"]
EXCLUDE= ["senior","lead","manager"]



def fetch_remoteok_jobs(): 
    
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
        seen_links.add(job_url)
        jobs.append({
            "title": job.get("position","N/A").strip(),
            "company": job.get("company", "N/A").strip(),
            "location":job.get("location").strip() or "Unknown",
            "link": job_url
        })
 
    return jobs



def filter_jobs(jobs):
    filtered= []
    for job in jobs:
        
        text = (job['title']+" "+ job['company']+" "+ job['location']).lower()
        if any(keyword in text for keyword in KEYWORDS) and not any(e in text for e in EXCLUDE):
            filtered.append(job)
    return filtered
    


def run_scraper_once():

    try:
            jobs= fetch_remoteok_jobs()
            conn= get_connection()
            cursor= conn.cursor()
            added= 0
            cursor.execute("select link from jobs")
            rows= cursor.fetchall()
            existing_links= {row['link'] for row in rows}


            new_jobs=[]

            for job in jobs:
                if job['link'] not  in existing_links:
                    new_jobs.append(job)
                

            for job in new_jobs:
                cursor.execute(
                    "Insert into jobs (title,company,location,link) values (?,?,?,?)",
                    (job['title'],job['company'],job['location'],job['link']))
                
                added+=1
            conn.commit()
            filtered_jobs = filter_jobs(new_jobs)

            if len(filtered_jobs) >0:
                send_telegram_alert(filtered_jobs)

            conn.close()
            return(f"Fetched {len(jobs)} jobs | New: {added}")
    except Exception as e:
        print("Error: ",e)
        return {"message": f"Scrape failed: {e}"}
    



