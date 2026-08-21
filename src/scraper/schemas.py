from datetime import datetime
from pydantic import BaseModel

class Job(BaseModel):
    title: str
    company: str
    location: str
    posted_at: datetime | None
    link: str
    source: str

class ScraperResponse(BaseModel):
    jobs: list[Job]

