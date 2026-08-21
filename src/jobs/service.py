from math import ceil

from sqlalchemy import select,or_,func
from sqlalchemy.orm import Session
from fastapi import HTTPException,status

from src.models import Jobs
from src.enums import JobsSortField,SortOrder,Source


class JobService:

    def get_jobs(self,
                title:str,
                company:str,
                location:str,
                source:Source,
                keyword:str,
                sort_by:JobsSortField,
                sort_order:SortOrder,
                limit:int,
                page:int,
                db: Session):
        
        query=select(Jobs).where(Jobs.is_active == True)
        if title:
            query= query.where(Jobs.title.ilike(f"%{title}%"))
        
        if company:
            query= query.where(Jobs.company.ilike(f"%{company}%"))
            
        if location:
            query= query.where(Jobs.location.ilike(f"%{location}%"))
        
        if source:
            query= query.where(Jobs.source == source.value)

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
        

    def get_by_id(self,
                job_id: int,
                db: Session):
        job= db.scalar(select(Jobs).where(Jobs.id== job_id))
        if not job:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Job not found")

        return job