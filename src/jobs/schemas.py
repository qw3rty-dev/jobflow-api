from datetime import datetime

from pydantic import BaseModel,ConfigDict


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    posted_at: datetime|None
    link: str
    source: str
    is_active: bool
    created_at: datetime
    last_seen: datetime
    valid_until: datetime
    model_config= ConfigDict(from_attributes=True)

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
