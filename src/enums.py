from enum import Enum

class Status(str,Enum):
    saved= "saved"
    applied= "applied"
    interview= "interview"
    offer= "offer"
    rejected= "rejected"

class JobsSortField(str,Enum):
    posted_at = "posted_at"
    valid_until = "valid_until"
    company = "company"
    location= "location"
    
class SortOrder(str,Enum):
    asc = "asc"
    desc = "desc"

class UserSortField(str,Enum):
    id = "id"
    username = "username"
    email = "email"
    created_at = "created_at"
    last_login = "last_login"

class SavedJobsSort(str,Enum):
    id = "id"
    saved_at = "saved_at"
    # posted_at = "Jobs.posted_at"
    applied_at = "applied_at"

class Source(str,Enum):
    adzuna = "adzuna"
    arbeitnow = "arbeitnow"
    greenhouse = "greenhouse"
    python_org = "python.org"
    remoteOK = "remoteOK"


