from math import ceil

from sqlalchemy import select,or_,func
from sqlalchemy.orm import Session
from fastapi import APIRouter,HTTPException,Depends,Query,status

from models import Jobs
from database import get_db
from enums import SortField,SortOrder
from schemas import GetResponse,JobResponse

router= APIRouter(prefix="/jobs",tags=["Jobs"])


@router.get("/",response_model=GetResponse)
def get_jobs(title:str=Query(default=None),
             company:str=Query(default=None),
             location:str=Query(default=None),
             source:str=Query(default=None),
             keyword:str=Query(default=None),
             sort_by:SortField=Query(default=SortField.posted_at),
             sort_order:SortOrder=Query(default=SortOrder.desc),
             limit:int = Query(default= 20, ge=1, le= 100),
             page:int= Query(default=1, ge=1),
             db: Session = Depends(get_db)):
    
    query=select(Jobs)
    if title:
        query= query.where(Jobs.title.ilike(f"%{title}%"))
    
    if company:
        query= query.where(Jobs.company.ilike(f"%{company}%"))
        
    if location:
        query= query.where(Jobs.location.ilike(f"%{location}%"))
    
    if source:
        query= query.where(Jobs.source.ilike(f"%{source}%"))

    if keyword:
        query= query.where(or_(Jobs.title.ilike(f"%{keyword}%"),Jobs.company.ilike(f"%{keyword}%"),Jobs.location.ilike(f"%{keyword}%"),Jobs.source.ilike(f"%{keyword}%")))
    
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    sort_expression = getattr(Jobs,sort_by.value)
    order = sort_expression.asc() if sort_order == SortOrder.asc else sort_expression.desc()
    offset= (page-1)* limit
    query= query.limit(limit).offset(offset)
    
    jobs = db.scalars(query.order_by(order)).all()
    total_pages= ceil(total/limit)
    

    meta = {
        "page": page,
        "limit": limit,
        "total":total,
        "total_pages": total_pages,
        "has_next": page<total_pages,
        "has_previous": page>1
    }

    return {"meta":meta,
            "jobs": jobs}
    

@router.get("/{job_id}",response_model= JobResponse)
def get_by_id(job_id: int,
              db: Session= Depends(get_db)):
    job= db.scalar(select(Jobs).where(Jobs.id== job_id))
    if not job:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Job not found")

    return job