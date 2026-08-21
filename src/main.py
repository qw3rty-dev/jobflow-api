import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.jobs.router import router as jobs_router
from src.user.router import router as user_router
from src.home.router import router as home_router
from src.admin.router import router as admin_router
from src.scraper.manager import background_scraper
from src.services.notification_worker import notification_worker




@asynccontextmanager
async def lifespan(app: FastAPI):
    
    scraper_task = asyncio.create_task(background_scraper())
    notification_task = asyncio.create_task(notification_worker())
    yield
    scraper_task.cancel()
    notification_task.cancel()
    print("App shutting down....")


app= FastAPI(title= "JobFlow API",
             version= "2.0.0",
             description= "Automated job discovery, tracking, notifications, exports and recommendations.",
             lifespan=lifespan)

app.include_router(jobs_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(home_router)


