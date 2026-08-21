from .schemas import HomeResponse
from fastapi import APIRouter


router = APIRouter()

@router.get("/",response_model=HomeResponse,include_in_schema=False)
def home():
    return HomeResponse(
        name= "JobFlow API",
        version= "2.0.0",
        description= "Backend API for automated job discovery, tracking and recommendations.",
        status= "running",
        documentation= "/docs"
    )