from datetime import datetime,UTC,timedelta

from sqlalchemy import select

from models import Jobs
from scraper.utils import normalize_job
    

def insert_or_update_jobs(db,jobs):
    existing_jobs= {job.link:job for job in db.scalars(select(Jobs)).all()}
    new_jobs = []
    updated= 0

    for job in jobs:
        if job.link not in existing_jobs:
            new_jobs.append(normalize_job(job)) 
        else:
            db_job = existing_jobs[job.link]
            db_job.valid_until = datetime.now(UTC)+ timedelta(days=30)
            db_job.is_active = True
            db_job.last_seen = datetime.now(UTC)
            updated += 1
    db.commit()

    for job in new_jobs:

        new_job = Jobs(**job.model_dump())
        db.add(new_job)
        
    db.commit()

    return {
        "added": len(new_jobs),
        "updated":updated
    }
