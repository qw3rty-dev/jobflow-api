from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends,Query,status

from src.database import get_db
from src.enums import UserSortField,SortOrder
from src.models import User
from src.security.jwt_handler import get_current_admin
from .schemas import StatsResponse,JobFlowScrapeResponse,CleanupResponse,DetailedUserResponse
from .service import AdminService
router= APIRouter(prefix="/admin",tags=["Admin"])


admin_service = AdminService()

@router.get("/users",response_model=list[DetailedUserResponse],status_code=status.HTTP_200_OK)
def get_users(id: int= Query(default=None),
              username: str= Query(default=None),
              email: str= Query(default=None),
              verified: bool= Query(default=None),
              admin: bool= Query(default=None),
              deleted: bool= Query(default=None),
              sort_by: UserSortField = Query(default=UserSortField.created_at),
              sort_order: SortOrder = Query(default= SortOrder.desc),
              limit:int = Query(default= 20, ge=1, le= 100),
              page:int= Query(default=1, ge=1),
              current_admin: User = Depends(get_current_admin),
              db:Session = Depends(get_db)):
    
    users = admin_service.get_users(
                id=id,
                username=username,
                email=email,
                verified=verified,
                admin=admin,
                deleted=deleted,
                sort_by=sort_by,
                sort_order=sort_order,
                limit=limit,
                page=page,
                current_admin=current_admin,
                db=db)
    
    return users


@router.get("/stats",response_model=StatsResponse,status_code=status.HTTP_200_OK)
def stats(db:Session = Depends(get_db),
          current_admin: User = Depends(get_current_admin)):
    
    stats = admin_service.stats(db=db,
                                current_admin=current_admin)
    return stats


@router.post("/scrape",response_model=JobFlowScrapeResponse,status_code=status.HTTP_200_OK)
async def manual_scrape(current_admin: User = Depends(get_current_admin)):
    result = await admin_service.manual_scrape(current_admin=current_admin)
    return result


@router.post("/cleanup",response_model=CleanupResponse,status_code=status.HTTP_200_OK)
def cleanup(db:Session = Depends(get_db),
            current_admin: User = Depends(get_current_admin)):
    return admin_service.cleanup(db=db,current_admin=current_admin)
    



