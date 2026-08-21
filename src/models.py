from datetime import datetime,UTC,timedelta

from sqlalchemy import ForeignKey,UniqueConstraint,DateTime,String
from sqlalchemy.orm import mapped_column,Mapped,relationship
from sqlalchemy.dialects.postgresql import ARRAY

from src.database import Base
from src.enums import Status


class Jobs(Base):

    __tablename__ = "jobs"
    id: Mapped[int]= mapped_column(primary_key= True)
    title: Mapped[str]= mapped_column(nullable= False)
    company: Mapped[str]= mapped_column(nullable= False)
    location: Mapped[str]= mapped_column(nullable= False)
    posted_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
    link: Mapped[str]= mapped_column(unique= True)
    source: Mapped[str]= mapped_column(nullable= False)
    is_active: Mapped[bool]= mapped_column(nullable= False,default=True)
    valid_until: Mapped[datetime]= mapped_column(DateTime(timezone=True),default= lambda:datetime.now(UTC)+timedelta(days=30))
    created_at: Mapped[datetime]= mapped_column(DateTime(timezone=True),nullable=False,default= lambda: datetime.now(UTC))
    last_seen: Mapped[datetime]= mapped_column(DateTime(timezone=True),nullable= False,default=lambda: datetime.now(UTC))
    is_notification_processed: Mapped[bool]= mapped_column(default=False)
    saved_by: Mapped[list["SavedJobs"]]= relationship(back_populates= "job")

    
class User(Base):

    __tablename__ = "users"
    id: Mapped[int]= mapped_column(primary_key= True)
    username: Mapped[str]= mapped_column(unique= True, nullable=False)
    email: Mapped[str]= mapped_column(unique= True, nullable= False)
    password_hash: Mapped[str]= mapped_column(nullable= False)
    created_at: Mapped[datetime]= mapped_column(DateTime(timezone=True),nullable= False,default= lambda: datetime.now(UTC))
    last_login: Mapped[datetime | None]= mapped_column(DateTime(timezone=True),nullable=True)
    is_admin: Mapped[bool]= mapped_column(default= False)
    is_verified: Mapped[bool]= mapped_column(default= False)
    notifications_enabled: Mapped[bool]= mapped_column(default=False)
    preferred_locations: Mapped[list[str]]= mapped_column(ARRAY(String),default=list,nullable=True)
    verification_code: Mapped[str|None]= mapped_column(nullable=True)
    verification_expires_at: Mapped[datetime|None]= mapped_column(DateTime(timezone=True),nullable=True)
    is_deleted: Mapped[bool]= mapped_column(default=False)
    deleted_at: Mapped[datetime|None]= mapped_column(DateTime(timezone=True),nullable=True)
    saved_jobs: Mapped[list["SavedJobs"]] = relationship(back_populates= "user")
    keywords: Mapped[list["Keywords"]] = relationship(back_populates= "user")


class Keywords(Base):

    __tablename__ = "keywords"
    __table_args__ = (UniqueConstraint("user_id","keyword"),)
    id: Mapped[int]= mapped_column(primary_key= True)
    user_id: Mapped[int]= mapped_column(ForeignKey("users.id"),nullable= False)
    keyword: Mapped[str]= mapped_column(nullable= False)
    user: Mapped["User"] = relationship(back_populates= "keywords")

    
class SavedJobs(Base):

    __tablename__ = "savedjobs"
    __table_args__ = (UniqueConstraint("user_id","job_id"),)
    id: Mapped[int]= mapped_column(primary_key= True)
    user_id: Mapped[int]= mapped_column(ForeignKey("users.id"),nullable= False)
    job_id: Mapped[int]= mapped_column(ForeignKey("jobs.id"),nullable= False)
    status: Mapped[Status]= mapped_column(nullable=False,default= Status.saved)
    notes: Mapped[str| None]= mapped_column(nullable= True)
    saved_at: Mapped[datetime]= mapped_column(DateTime(timezone=True),default= lambda: datetime.now(UTC))
    applied_at: Mapped[datetime | None]= mapped_column(DateTime(timezone=True),nullable= True)
    user: Mapped["User"] = relationship(back_populates= "saved_jobs")
    job: Mapped["Jobs"] = relationship(back_populates= "saved_by")


    