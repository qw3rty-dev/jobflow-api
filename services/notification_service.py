from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import User,Jobs
from .email_service import send_notification_email




def find_matching_jobs(user,jobs):

    matched_jobs =[]
    
    for job in jobs:
        searchable = " ".join([job.title or "",
                                job.company or "",
                                job.location or "",
                                job.source or ""]).lower()
        for keyword in user.keywords:
            if keyword.keyword.lower() in searchable:
                matched_jobs.append(job)
                break
    return matched_jobs


def send_notifications(db):

    jobs=db.scalars(select(Jobs).where(Jobs.is_notification_processed == False)).all()
    if not jobs:
        return
    
    users= db.scalars(select(User).options(selectinload(User.keywords)).where(User.is_verified ==True,User.notifications_enabled == True)).all()
    if not users:
        return
    
    for user in users:
        if not user.keywords:
            continue

        matched_jobs = find_matching_jobs(user,jobs)
        if matched_jobs:
            send_notification_email(user,matched_jobs)

    for job in jobs:
        job.is_notification_processed = True
    db.commit()

