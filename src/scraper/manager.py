import json
import asyncio
from pathlib import Path
from datetime import datetime,UTC,timedelta

from src.database import sessionLocal
from .sources.adzuna import fetch_adzuna_jobs
from .utils import last_clean_up,save_last_cleanup
from .sources.remoteOK import fetch_remoteok_jobs
from .sources.python_jobs import fetch_python_jobs
from .sources.arbeitnow import fetch_arbeitnow_jobs
from .sources.greenhouse import fetch_greenhouse_jobs
from src.services.cleanup_service import cleanup_expired_job
from src.services.job_insert_update import insert_or_update_jobs



async def scrap_all_sources():

    jobs = []
    print("Refreshing....")
    adzuna_jobs = await fetch_adzuna_jobs()
    remoteOK_jobs = fetch_remoteok_jobs()
    arbeitnow_jobs = fetch_arbeitnow_jobs()
    python_jobs = fetch_python_jobs()
    greenhouse_jobs = fetch_greenhouse_jobs()

    jobs.extend(adzuna_jobs.jobs)
    jobs.extend(remoteOK_jobs.jobs)
    jobs.extend(arbeitnow_jobs.jobs)
    jobs.extend(python_jobs.jobs)
    jobs.extend(greenhouse_jobs.jobs)

    return jobs
          
async def sync_jobs():
    
    db = None
    try:
        jobs= await scrap_all_sources()
        db= sessionLocal()
        result = insert_or_update_jobs(db,jobs)
        
        cleanup_result = {
            "jobs_deleted": 0,
            "marked_inactive": 0,
            "deactivated_accounts_deleted": 0,
            "unverified_accounts_deleted": 0
        }
        if datetime.now(UTC) - last_clean_up() >= timedelta(days=1):
            cleanup_result= cleanup_expired_job(db)
            save_last_cleanup()


        print(f"""
        New : {result["added"]}
        Updated: {result["updated"]}
        Deleted: {cleanup_result["jobs_deleted"]}
        Marked inactive: {cleanup_result["marked_inactive"]}
        Deactivated accounts deleted: {cleanup_result["deactivated_accounts_deleted"]}
        Unverified accounts deleted : {cleanup_result["unverified_accounts_deleted"]}
        """)
        
        return {
            "new" : result["added"],
            "updated": result["updated"],
            "deleted": cleanup_result["jobs_deleted"],
            "marked_inactive": cleanup_result["marked_inactive"],
            "deactivated_accounts_deleted": cleanup_result["deactivated_accounts_deleted"],
            "unverified_accounts_deleted": cleanup_result["unverified_accounts_deleted"]
        }

    except Exception as e:
        print(f"Error: {e}")
        print("manager")
        raise
    
    finally:
        if db:
         db.close()
    



PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

SCRAPER_INTERVAL = config["scraper_interval"]



async def background_scraper():
    while True:
        try:
          await sync_jobs()
        except Exception as e:
            print(e)
        await asyncio.sleep(SCRAPER_INTERVAL)
