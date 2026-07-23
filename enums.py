from enum import Enum

class Status(str,Enum):
    saved= "saved"
    applied= "applied"
    interview= "interview"
    offer= "offer"
    rejected= "rejected"

class SortField(str,Enum):
    posted_at = "posted_at"
    valid_until = "valid_until"
    company = "company"
    location= "location"
    
class SortOrder(str,Enum):
    asc = "asc"
    desc = "desc"