from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends,Query,status

from src.database import get_db
from src.enums import JobsSortField,SortOrder,Source
from .schemas import GetResponse,JobResponse
from .service import JobService

router= APIRouter(prefix="/jobs",tags=["Jobs"])


job_service = JobService()

@router.get("/",response_model=GetResponse,status_code=status.HTTP_200_OK)
def get_jobs(title:str=Query(default=None),
             company:str=Query(default=None),
             location:str=Query(default=None),
             source:Source=Query(default=None),
             keyword:str=Query(default=None),
             sort_by:JobsSortField=Query(default=JobsSortField.posted_at),
             sort_order:SortOrder=Query(default=SortOrder.desc),
             limit:int = Query(default= 20, ge=1, le= 100),
             page:int= Query(default=1, ge=1),
             db: Session = Depends(get_db)):
    
   

    return job_service.get_jobs(
                    title=title,
                    company=company,
                    location=location,
                    source=source,
                    keyword=keyword,
                    sort_by=sort_by,
                    sort_order=sort_order,
                    limit=limit,
                    page=page,
                    db=db)
    

@router.get("/{job_id}",response_model= JobResponse,status_code=status.HTTP_200_OK)
def get_by_id(job_id: int,
              db: Session= Depends(get_db)):
    job= job_service.get_by_id(job_id=job_id,
                               db=db)
    return job