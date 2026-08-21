from datetime import datetime

from pydantic import BaseModel,ConfigDict,EmailStr


class JobFlowScrapeResponse(BaseModel):
    new: int
    updated: int
    deleted: int
    marked_inactive: int

class CleanupResponse(BaseModel):
    jobs_deleted: int
    marked_inactive: int
    deactivated_accounts_deleted: int
    unverified_accounts_deleted: int

class StatsResponse(BaseModel):
    total_jobs: int
    active_jobs: int
    inactive_jobs: int
    total_users: int
    verified_users: int
    total_saved_jobs: int
    total_keywords: int 
    source_count: int
    sources: list

class DetailedUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    last_login: datetime| None
    is_verified: bool
    is_admin: bool
    notifications_enabled: bool 
    is_deleted: bool
    deleted_at: datetime| None
    model_config= ConfigDict(from_attributes=True)
