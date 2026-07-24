import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from schemas import HomeResponse
from routes import jobs,auth,user,admin
from scraper.manager import background_scraper
from services.notification_worker import notification_worker




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

app.include_router(jobs.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)


@app.get("/",response_model=HomeResponse,include_in_schema=False)
def home():
    return HomeResponse(
        name= "JobFlow API",
        version= "2.0.0",
        description= "Backend API for automated job discovery, tracking and recommendations.",
        status= "running",
        documentation= "/docs"
    )
