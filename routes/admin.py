from sqlalchemy import select,func
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends

from database import get_db
from models import User,Jobs,SavedJobs,Keywords
from security.jwt_handler import get_current_admin
from scraper.manager import sync_jobs,cleanup_expired_job
from schemas import StatsResponse,JobFlowScrapeResponse,CleanupResponse

router= APIRouter(prefix="/admin",tags=["Admin"])



@router.post("/scrape",response_model=JobFlowScrapeResponse)
async def manual_scrape(current_admin: User = Depends(get_current_admin)):
    result = await sync_jobs()
    return result


@router.post("/cleanup",response_model=CleanupResponse)
def cleanup(db:Session = Depends(get_db),
            current_admin: User = Depends(get_current_admin)):
    return cleanup_expired_job(db)
    

@router.get("/stats",response_model=StatsResponse)
def stats(db:Session = Depends(get_db),
          current_admin: User = Depends(get_current_admin)):
    
    total_jobs = db.scalar(select(func.count(Jobs.id)))
    active_jobs = db.scalar(select(func.count(Jobs.id)).where(Jobs.is_active == True))
    inactive_jobs = db.scalar(select(func.count(Jobs.id)).where(Jobs.is_active == False))
    total_users = db.scalar(select(func.count(User.id)))
    total_saved_jobs = db.scalar(select(func.count(SavedJobs.id)))
    total_keywords = db.scalar(select(func.count(Keywords.id)))
    sources = db.scalars(select(Jobs.source).distinct()).all()
    return {
        "total_jobs":total_jobs,
        "active_jobs": active_jobs,
        "inactive_jobs": inactive_jobs,
        "total_users": total_users,
        "total_saved_jobs": total_saved_jobs,
        "total_keywords":total_keywords,
        "source_count": len(sources),
        "sources": sources 
    }


