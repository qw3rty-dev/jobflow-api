from datetime import datetime,UTC

from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from fastapi import APIRouter,Depends,status,Query

from src.models import User
from src.database import get_db
from .service import UserService
from src.jobs.schemas import JobResponse
from src.auth.schemas import UserResponse
from src.enums import Status,SavedJobsSort,SortOrder
from src.security.jwt_handler import get_current_user,get_current_verified_user
from .schemas import SaveJobsResponse,UpdateSavedJob,DashboardResponse,KeywordResponse,UserPreferencesUpdate

router= APIRouter(prefix="/user",tags=["Users"])

user_service = UserService()

@router.post("/save/{job_id}",response_model=SaveJobsResponse,status_code=status.HTTP_201_CREATED)
def save_job(job_id: int,
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):
    job = user_service.save_job(job_id=job_id,
                                current_user=current_user,
                                db=db)
    
    return job


@router.post("/keywords",response_model=KeywordResponse,status_code=status.HTTP_201_CREATED)
def add_keyword(keyword:str,
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):

    keyword = user_service.add_keyword(keyword=keyword,
                                     current_user=current_user,
                                     db=db)
    return keyword


@router.get("/",response_model= list[SaveJobsResponse],status_code=status.HTTP_200_OK)
def get_saved_jobs(status: Status = Query(default=None),
                   search: str = Query(default=None),
                   active: bool = Query(default=None),
                   sort_by: SavedJobsSort = Query(default=SavedJobsSort.saved_at),
                   sort_order: SortOrder = Query(default=SortOrder.desc),
                   limit:int = Query(default= 20, ge=1, le= 100),
                   page:int= Query(default=1, ge=1),
                   current_user: User = Depends(get_current_verified_user),
                   db: Session= Depends(get_db)):

    jobs = user_service.get_saved_jobs(
                    status=status,
                    search=search,
                    active=active,
                    sort_by=sort_by,
                    sort_order=sort_order,
                    limit=limit,
                    page=page,
                    current_user=current_user,
                    db=db)

    return jobs


@router.get("/keywords",response_model= list[KeywordResponse],status_code=status.HTTP_200_OK)
def get_keywords(
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):
        
    keywords = user_service.get_keywords(current_user=current_user,
                                         db=db)
    return keywords


@router.get("/me",response_model=UserResponse,status_code=status.HTTP_200_OK)
def get_me(current_user:User = Depends(get_current_user)):

    return user_service.get_me(current_user=current_user)


@router.get("/dashboard",response_model=DashboardResponse,status_code=status.HTTP_200_OK)
def dashboard(
            current_user: User = Depends(get_current_verified_user),
            db: Session= Depends(get_db)):
        
    dashboard = user_service.dashboard(current_user=current_user,
                                       db=db)
    return dashboard


@router.get("/recommended",response_model=list[JobResponse],status_code=status.HTTP_200_OK)
def recommendations(
                  current_user: User = Depends(get_current_verified_user),
                  db:Session = Depends(get_db)):
    jobs = user_service.recommendations(current_user=current_user,
                                        db=db)
    return jobs


@router.patch("/edit/{id}",response_model=SaveJobsResponse,status_code=status.HTTP_200_OK)
def edit_savedjobs(id:int,
                  update:UpdateSavedJob,
                  current_user: User = Depends(get_current_verified_user),
                  db:Session = Depends(get_db)):
        
    job = user_service.edit_savedjobs(id=id,
                                      update=update,
                                      current_user=current_user,
                                      db=db)
    return job    
    
@router.patch("/me/preferences",response_model= UserResponse,status_code=status.HTTP_200_OK)
def edit_preferences(update: UserPreferencesUpdate,
                     current_user: User = Depends(get_current_verified_user),
                     db:Session = Depends(get_db)):
    
    

    return user_service.edit_preferences(update=update,
                                         current_user=current_user,
                                         db=db)


@router.delete("/remove/{id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_savedjob(id:int,
                    current_user: User =Depends(get_current_verified_user),
                    db:Session = Depends(get_db)):
        
   user_service.remove_savedjob(id=id,
                                current_user=current_user,
                                db=db)

    
    
@router.delete("/delete/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(id:int,
                current_user: User = Depends(get_current_verified_user),
                db:Session = Depends(get_db)):
        
    user_service.delete_keyword(id=id,
                                current_user=current_user,
                                db=db)




@router.get("/export_pdf",response_class=StreamingResponse,status_code=status.HTTP_200_OK)
def export_to_pdf(
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):
     

    return user_service.export_to_pdf(current_user=current_user,
                                      db=db)

@router.get("/export_csv",response_class=StreamingResponse,status_code=status.HTTP_200_OK)
def export_to_csv(
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):
        
    return user_service.export_to_csv(current_user=current_user,
                                      db=db)


@router.get("/{job_id}",response_model= SaveJobsResponse,status_code=status.HTTP_200_OK)
def get_saved_job_by_id(job_id:int,
             current_user: User = Depends(get_current_verified_user),
             db: Session= Depends(get_db)):
        
    job = user_service.get_saved_job_by_id(job_id=job_id,
                                           current_user=current_user,
                                           db=db)
    return job
