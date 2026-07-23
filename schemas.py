from datetime import datetime

from pydantic import BaseModel,ConfigDict,EmailStr,Field

from enums import Status


#--------------------- Home ---------------------


class HomeResponse(BaseModel):
    name: str
    version: str
    description: str
    status: str
    documentation: str


# -------------------Scraper--------------------------


class Job(BaseModel):
    title: str
    company: str
    location: str
    posted_at: datetime | None
    link: str
    source: str

class ScraperResponse(BaseModel):
    jobs: list[Job]


# ----------------------------Jobs Route ---------------------------------


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    posted_at: datetime
    link: str
    source: str
    is_active: bool
    created_at: datetime
    last_seen: datetime
    valid_until: datetime
    # model_config= ConfigDict(from_attributes=True)

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool 
    has_previous: bool 

class GetResponse(BaseModel):
    meta: PaginationMeta
    jobs: list[JobResponse]


# -------------------------- Authentication --------------------------


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8,max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    last_login: datetime| None
    is_verified: bool
    notifications_enabled: bool 


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8,max_length=128)


class VerifyOTP(BaseModel):
    otp: str = Field(min_length=6,max_length=6)


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6,max_length=6)
    new_password: str = Field(min_length=8,max_length=128)


# ------------------------------ SavedJobs ----------------------------------


class JobSummaryResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    posted_at: datetime
    link: str
    source: str
    is_active: bool
    last_seen: datetime


class SaveJobsResponse(BaseModel):
    id: int
    status: Status
    notes: str| None
    saved_at: datetime
    applied_at: datetime | None
    job : JobSummaryResponse


class UpdateSavedJob(BaseModel):
    status: Status = Status.saved
    notes: str|None= None


class UserPreferencesUpdate(BaseModel):
    notifications_enabled: bool


class MessageResponse(BaseModel):
    message: str


class DashboardResponse(BaseModel):
    total_jobs: int
    saved_jobs: int
    applied: int
    interview: int
    rejected: int
    added_today: int


class KeywordResponse(BaseModel):
    id: int
    keyword: str

 #--------------------------Admin---------------------------


class JobFlowScrapeResponse(BaseModel):
    new: int
    updated: int
    deleted: int
    marked_inactive: int

class CleanupResponse(BaseModel):
    marked_inactive: int
    deleted: int
    unverified_accounts_deleted: int

class StatsResponse(BaseModel):
    total_jobs: int
    active_jobs: int
    inactive_jobs: int
    total_users: int
    total_saved_jobs: int
    total_keywords: int 
    source_count: int
    sources: list