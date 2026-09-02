from datetime import datetime,UTC

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session,selectinload
from fastapi.responses import StreamingResponse
from sqlalchemy import select,or_,func,cast,Date
from fastapi import HTTPException,status

from src.models import Jobs,Keywords,SavedJobs,User
from src.enums import Status,SavedJobsSort,SortOrder
from .schemas import UpdateSavedJob,UserPreferencesUpdate
from src.services.export_service import generate_pdf,generate_csv
from src.services.recommendation_service import get_recommendations


class UserService:

    def save_job(self,
                job_id: int,
                current_user: User,
                db: Session):
        
        if not db.scalar(select(Jobs).where(Jobs.id == job_id)):
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Job not found")
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


    def add_keyword(self,
                    keyword:str,
                    current_user: User,
                    db: Session):

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


    def get_saved_jobs(self,
                    status: Status,
                    search: str,
                    active: bool,
                    sort_by: SavedJobsSort,
                    sort_order: SortOrder,
                    limit:int,
                    page:int,
                    current_user: User,
                    db: Session):

        query= select(SavedJobs).join(SavedJobs.job).options(selectinload(SavedJobs.job)).where(SavedJobs.user_id == current_user.id)
        if status:
            query = query.where(SavedJobs.status == status.value)
        if active is not None:
            query = query.where(Jobs.is_active == active)
        if search:
            query= query.where(or_(Jobs.title.ilike(f"%{search}%"),Jobs.company.ilike(f"%{search}%"),Jobs.location.ilike(f"%{search}%"),Jobs.source.ilike(f"%{search}%"),SavedJobs.notes.ilike(f"%{search}%")))

        sort_expression = getattr(SavedJobs,sort_by.value)
        order = sort_expression.asc() if sort_order == SortOrder.asc else sort_expression.desc()

        offset= (page-1)* limit
        query= query.limit(limit).offset(offset)

        jobs = db.scalars(query.order_by(order)).all()

        return jobs


    def get_keywords(self,
                current_user: User,
                db: Session):
            
        keywords = db.scalars(select(Keywords).where(Keywords.user_id == current_user.id)).all()

        return keywords


    def get_me(self,current_user:User):

        return current_user


    def dashboard(self,
                current_user: User,
                db: Session):
            
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


    def recommendations(self,
                    current_user: User,
                    db:Session):
        jobs = get_recommendations(current_user,db)
        return jobs


    def edit_savedjobs(self,
                    id:int,
                    update:UpdateSavedJob,
                    current_user: User,
                    db:Session):
            
        job = db.scalar(select(SavedJobs).where(SavedJobs.id==id,SavedJobs.user_id==current_user.id))
        if not job:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Job not found")
        update= update.model_dump(exclude_unset=True)
        new_status = update.get("status")
        if new_status:
            if new_status == Status.applied and job.status != "applied":
                job.applied_at = datetime.now(UTC)
            elif new_status != Status.applied and job.status == "applied":
                job.applied_at = None
        for field,value in update.items():
            setattr(job,field,value)

        db.commit()
        return job    
        
    def edit_preferences(self,
                        update: UserPreferencesUpdate,
                        current_user: User,
                        db:Session):
        
        update = update.model_dump(exclude_unset=True)

        for field,value in update.items():
            setattr(current_user,field,value)
        db.commit()

        return current_user


    def remove_savedjob(self,
                        id:int,
                        current_user: User,
                        db:Session):
            
        job = db.scalar(select(SavedJobs).where(SavedJobs.id==id,SavedJobs.user_id==current_user.id))

        if not job:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Job not found")
        db.delete(job)
        db.commit()

        
        
    def delete_keyword(self,
                    id:int,
                    current_user: User,
                    db:Session):
            
        keyword= db.scalar(select(Keywords).where(Keywords.id == id,Keywords.user_id == current_user.id))

        if not keyword:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Keyword not found")
        
        db.delete(keyword)
        db.commit()



    def export_to_pdf(self,
                    current_user: User,
                    db: Session):
        
        jobs = db.scalars(select(SavedJobs).options(selectinload(SavedJobs.job)).where(SavedJobs.user_id == current_user.id)).all()

        pdf_buffer = generate_pdf(current_user,jobs)

        return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="jobflow_export.pdf"'
        })


    def export_to_csv(self,
                current_user: User,
                db: Session):
            
        jobs = db.scalars(select(SavedJobs).options(selectinload(SavedJobs.job)).where(SavedJobs.user_id == current_user.id)).all()

        csv_buffer = generate_csv(jobs)

        return StreamingResponse(
        csv_buffer,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="jobflow_export.csv"'
        })


    def get_saved_job_by_id(self,
                            job_id:int,
                            current_user: User,
                            db: Session):
            
        job = db.scalar(select(SavedJobs).where(SavedJobs.id == job_id).where(SavedJobs.user_id == current_user.id))
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= "Job not found")

        return job
