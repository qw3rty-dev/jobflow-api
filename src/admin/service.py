from sqlalchemy import select,func
from sqlalchemy.orm import Session

from src.enums import UserSortField,SortOrder
from src.models import User,Jobs,SavedJobs,Keywords
from src.scraper.manager import sync_jobs
from src.services.cleanup_service import cleanup_expired_job


class AdminService:

    def get_users(self,
                id: int,
                username: str,
                email: str,
                verified: bool,
                admin: bool,
                deleted: bool,
                sort_by: UserSortField,
                sort_order: SortOrder,
                limit: int,
                page: int,
                current_admin: User,
                db:Session):
        
        query = select(User)
        if id:
            query = query.where(User.id == id)
        if username:
            query = query.where(User.username.ilike(f"%{username}%"))
        if email:
            query = query.where(User.email.ilike(f"%{email}%"))
        if verified is not None:
            query = query.where(User.is_verified == verified)
        if admin is not None:
            query = query.where(User.is_admin == admin)
        if deleted is not None:
            query = query.where(User.is_deleted == deleted)


        sort_expression = getattr(User,sort_by.value)
        order = sort_expression.asc() if sort_order == SortOrder.asc else sort_expression.desc()

        offset= (page-1)* limit
        query= query.limit(limit).offset(offset)

        users = db.scalars(query.order_by(order)).all()
        return users

    def stats(self,
            db:Session,
            current_admin: User):
        total_jobs = db.scalar(select(func.count(Jobs.id)))
        active_jobs = db.scalar(select(func.count(Jobs.id)).where(Jobs.is_active == True))
        inactive_jobs = db.scalar(select(func.count(Jobs.id)).where(Jobs.is_active == False))
        total_users = db.scalar(select(func.count(User.id)))
        verified_users = db.scalar(select(func.count(User.id)).where(User.is_verified == True))
        total_saved_jobs = db.scalar(select(func.count(SavedJobs.id)))
        total_keywords = db.scalar(select(func.count(Keywords.id)))
        sources = db.scalars(select(Jobs.source).distinct()).all()
        return {
            "total_jobs":total_jobs,
            "active_jobs": active_jobs,
            "inactive_jobs": inactive_jobs,
            "total_users": total_users,
            "verified_users": verified_users,
            "total_saved_jobs": total_saved_jobs,
            "total_keywords":total_keywords,
            "source_count": len(sources),
            "sources": sources 
        }
    async def manual_scrape(self,
                            current_admin: User):
        result = await sync_jobs()
        return result


    def cleanup(self,
                db:Session,
                current_admin: User):
        return cleanup_expired_job(db)
        



