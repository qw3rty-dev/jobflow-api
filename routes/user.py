from datetime import datetime,UTC

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session,selectinload
from fastapi.responses import StreamingResponse
from sqlalchemy import select,or_,func,cast,Date
from fastapi import APIRouter,HTTPException,Depends,status

from enums import Status
from database import get_db
from models import Jobs,Keywords,SavedJobs,User
from security.jwt_handler import get_current_user,get_current_verified_user
from services.export_service import generate_pdf,generate_csv
from schemas import SaveJobsResponse,UpdateSavedJob,MessageResponse,DashboardResponse,KeywordResponse,UserResponse,UserPreferencesUpdate


router= APIRouter(prefix="/user",tags=["Users"])


@router.post("/save/{job_id}",response_model=SaveJobsResponse)
def save_job(job_id: int,
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):
    
    job = SavedJobs(
                    user_id = current_user.id,
                    job_id = job_id
                    )
    try:
        db.add(job)
        db.commit()
        db.refresh(job)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code= status.HTTP_409_CONFLICT,detail ="Job already saved")
    
    return job


@router.post("/keywords",response_model=KeywordResponse)
def add_keyword(keyword:str,
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):

    keyword = Keywords(
                        user_id = current_user.id,
                        keyword = keyword
                       )
    try:
        db.add(keyword)
        db.commit()
        db.refresh(keyword)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail= "Keyword already exists")

    return keyword


@router.get("/",response_model= list[SaveJobsResponse])
def get_saved_jobs(
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):

    jobs = db.scalars(select(SavedJobs).options(selectinload(SavedJobs.job)).where(SavedJobs.user_id == current_user.id)).all()

    return jobs


@router.get("/keywords",response_model= list[KeywordResponse])
def get_keywords(
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):
        
    keywords = db.scalars(select(Keywords).where(Keywords.user_id == current_user.id)).all()

    return keywords


@router.get("/me",response_model=UserResponse)
def get_me(current_user:User = Depends(get_current_user)):

    return current_user


@router.get("/dashboard",response_model=DashboardResponse)
def dashboard(
            current_user: User = Depends(get_current_verified_user),
            db: Session= Depends(get_db)):
        
    total_jobs = db.scalar(select(func.count(Jobs.id)).where(Jobs.is_active == True))
    saved_jobs = db.scalar(select(func.count(SavedJobs.id)).where(SavedJobs.user_id ==current_user.id))
    applied = db.scalar(select(func.count(SavedJobs.id)).where(SavedJobs.status == Status.applied).where(SavedJobs.user_id ==current_user.id))
    interview = db.scalar(select(func.count(SavedJobs.id)).where(SavedJobs.status == Status.interview).where(SavedJobs.user_id ==current_user.id))
    rejected = db.scalar(select(func.count(SavedJobs.id)).where(SavedJobs.status == Status.rejected).where(SavedJobs.user_id ==current_user.id))
    added_today = db.scalar(select(func.count(SavedJobs.id)).where(cast(SavedJobs.saved_at,Date)== datetime.now(UTC).date()).where(SavedJobs.user_id ==current_user.id))

    return {"total_jobs": total_jobs,
            "saved_jobs": saved_jobs,
            "applied": applied,
            "interview": interview,
            "rejected": rejected,
            "added_today": added_today}
    


@router.patch("/edit/{id}",response_model=SaveJobsResponse)
def edit_savedjobs(id:int,
                  update:UpdateSavedJob,
                  current_user: User = Depends(get_current_verified_user),
                  db:Session = Depends(get_db)):
        
    job = db.scalar(select(SavedJobs).where(SavedJobs.id==id,SavedJobs.user_id==current_user.id))
    if not job:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Job not found")
    applied = True if job.status =="applied" else False
    update= update.model_dump(exclude_unset=True)
    for field,value in update.items():
        setattr(job,field,value)
    if not applied:    
        if job.status =="applied":
         job.applied_at = datetime.now(UTC)
    if applied:    
        if job.status !="applied":
         job.applied_at = None

    db.commit()

    return job    
    
@router.patch("/me/preferences",response_model= UserResponse)
def edit_preferences(update: UserPreferencesUpdate,
                     current_user: User = Depends(get_current_verified_user),
                     db:Session = Depends(get_db)):
    
    update = update.model_dump(exclude_unset=True)

    for field,value in update.items():
        setattr(current_user,field,value)
    db.commit()

    return current_user


@router.delete("/remove/{id}",response_model= MessageResponse)
def remove_savedjob(id:int,
                    current_user: User =Depends(get_current_verified_user),
                    db:Session = Depends(get_db)):
        
    job = db.scalar(select(SavedJobs).where(SavedJobs.id==id,SavedJobs.user_id==current_user.id))

    if not job:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Job not found")
    db.delete(job)
    db.commit()

    return {"message": "Job removed"}
    
    
@router.delete("/delete{id}",response_model=MessageResponse)
def delete_keyword(id:int,
                current_user: User = Depends(get_current_verified_user),
                db:Session = Depends(get_db)):
        
    keyword= db.scalar(select(Keywords).where(Keywords.id == id,Keywords.user_id == current_user.id))

    if not keyword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Keyword not found")
    
    db.delete(keyword)
    db.commit()

    return {"message": "Keyword removed"}




@router.get("/export_pdf",response_class=StreamingResponse)
def export_to_pdf(
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):
     
    jobs = db.scalars(select(SavedJobs).options(selectinload(SavedJobs.job)).where(SavedJobs.user_id == current_user.id)).all()

    pdf_buffer = generate_pdf(current_user,jobs)

    return StreamingResponse(
    pdf_buffer,
    media_type="application/pdf",
    headers={
        "Content-Disposition": 'attachment; filename="jobflow_export.pdf"'
    })


@router.get("/export_csv",response_class=StreamingResponse)
def export_to_csv(
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):
        
    jobs = db.scalars(select(SavedJobs).options(selectinload(SavedJobs.job)).where(SavedJobs.user_id == current_user.id)).all()

    csv_buffer = generate_csv(jobs)

    return StreamingResponse(
    csv_buffer,
    media_type="text/csv",
    headers={
        "Content-Disposition": 'attachment; filename="jobflow_export.csv"'
    })


@router.get("/{job_id}",response_model= SaveJobsResponse)
def get_saved_job_by_id(job_id:int,
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):
        
    job = db.scalar(select(SavedJobs).where(SavedJobs.id == job_id).where(SavedJobs.user_id == current_user.id))
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= "Job not found")

    return job
