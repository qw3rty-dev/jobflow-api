from fastapi import APIRouter,HTTPException
from database import get_connection
from models import Job
from scraper import run_scraper_once
from sqlite3 import IntegrityError
router= APIRouter(prefix="/jobs",tags=["Jobs"])

@router.post("/")
def create_job(job: Job):
    conn=get_connection()
    cursor= conn.cursor()

    try:
        cursor.execute("Insert into jobs (title,company,location,link) values(?,?,?,?)",
                       (job.title,job.company,job.location,job.link))
        conn.commit()
    except IntegrityError:
        raise HTTPException(status_code=409,detail="Job already exists")
    conn.close()
    return{"message":"Job added"}


@router.get("/")
def get_jobs(title:str=None,company:str=None,location:str=None):
    conn= get_connection()
    cursor= conn.cursor()
    query="select * from jobs"
    params= []
    if title or company or location:
        query+= " where "

    if title:
        query+= " title like ? "
        params.append(f"%{title}%")
    
    if company:
        if title:
            query+= " and "
        query+= " company like ? "
        params.append(f"%{company}%")

    if location:
        if title or company:
            query+= " and "
        query+= "location like ? "
        params.append(f"%{location}%")
    
    cursor.execute(query,params)
    rows= cursor.fetchall()
    conn.close()
    jobs=[]
    for row in rows:
        jobs.append({"id":row['id'],
                    "title":row['title'],
                    "company":row['company'],
                    "location":row['location'],
                    "link":row['link'],
                    "applied" : row['applied']
                     })
    
    return {"count":len(jobs),
            "data": jobs}
    

@router.post("/scrape")
def manual_scrape():
    return run_scraper_once()



@router.get("/stats")
def stats():
    conn= get_connection()
    cursor= conn.cursor()
    cursor.execute("select count(*) from jobs")
    total= cursor.fetchone()[0]
    cursor.execute("select count(*) from jobs where applied=1")
    applied=cursor.fetchone()[0]
    conn.close()
     
    return {
        "total": total,
        "applied": applied,
        "pending": total-applied
    }

@router.get("/{job_id}")
def get_by_id(job_id: int):
    conn= get_connection()
    cursor= conn.cursor()
    cursor.execute( "select * from jobs where id = ?",(job_id,))
    row= cursor.fetchone()
    conn.close()
    if row:
        return {"id":row['id'],
                        "title":row['title'],
                        "company":row['company'],
                        "location":row['location'],
                        "link":row['link'],
                        "applied":row['applied']}
    raise HTTPException(status_code=404,detail="Job not found")


@router.delete("/{job_id}")
def delete_job(job_id:int):
    conn= get_connection()
    cursor= conn.cursor()

    cursor.execute("delete from jobs where id= ?",(job_id,))
    conn.commit()
    if cursor.rowcount==0:
        conn.close()
        raise HTTPException(status_code=404,detail="Job not found")
    conn.close()
    return {"message":"Job deleted"}


@router.put("/{job_id}")
def mark_applied(job_id:int):
    conn= get_connection()
    cursor= conn.cursor()
    cursor.execute("update jobs set applied = 1 where id = ?",(job_id,))
    conn.commit()
    if cursor.rowcount== 0:
        conn.close()
        raise HTTPException(status_code=404,detail="Job not found")
    conn.close()
    return {"message":"marked as applied"}




