from src.models import SavedJobs,Jobs
from sqlalchemy import select
from sqlalchemy.orm import selectinload

def get_saved_jobs(user,db):
    saved_jobs= db.scalars(select(SavedJobs).join(SavedJobs.job).options(selectinload(SavedJobs.job)).where(SavedJobs.user_id == user.id)).all()
    return saved_jobs

def get_saved_title_words(saved_jobs):
    saved_title_words= set()
    for savedjob in saved_jobs:
        words = savedjob.job.title.lower().split() 
        saved_title_words.update(words)
    noisewords = {"and","or","the","a","an","of","in","at","for","with","to","/"}
    saved_title_words -= noisewords
    return saved_title_words

def score_job(job,saved_title_words,keywords,preferred_locations):
    score = 0
    keywords = [object.keyword for object in keywords]
    for keyword in keywords:
        if keyword.lower() in job.title.lower():
            score+=5
    for word in saved_title_words:
        if word in job.title.lower():
            score+=3

    if preferred_locations:
        for loc in preferred_locations:
            if loc.lower() in job.location.lower():
                score+=2
                break
    return score



def get_recommendations(user,db):

    recent_jobs = db.scalars(select(Jobs).where(Jobs.is_active==True).order_by(Jobs.posted_at.desc()).limit(100)).all()
    saved_jobs = get_saved_jobs(user,db)
    saved_title_words = get_saved_title_words(saved_jobs)
    scored = [(job,score_job(job,saved_title_words,user.keywords,user.preferred_locations)) for job in recent_jobs]

    scored.sort(key= lambda t: t[1],reverse=True)

    top_jobs = [job for job,score in scored if score >0][:10]

    return top_jobs
