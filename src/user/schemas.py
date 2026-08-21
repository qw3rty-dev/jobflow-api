from datetime import datetime

from pydantic import BaseModel,ConfigDict

from src.enums import Status


class JobSummaryResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    posted_at: datetime|None
    link: str
    source: str
    is_active: bool
    last_seen: datetime
    model_config= ConfigDict(from_attributes=True)


class SaveJobsResponse(BaseModel):
    id: int
    status: Status
    notes: str| None
    saved_at: datetime
    applied_at: datetime | None
    job : JobSummaryResponse


class UpdateSavedJob(BaseModel):
    status: Status|None = None
    notes: str|None= None
    model_config= ConfigDict(extra="forbid")


class UserPreferencesUpdate(BaseModel):
    notifications_enabled: bool= None
    preferred_locations: list[str]|None= None
    model_config= ConfigDict(extra="forbid")


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
    model_config= ConfigDict(from_attributes=True)
