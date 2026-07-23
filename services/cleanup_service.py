from datetime import datetime,UTC,timedelta

from sqlalchemy import update,delete,select

from models import Jobs,SavedJobs,User


def cleanup_expired_job(db):

    now =datetime.now(UTC)
    cutoff = now - timedelta(days=30)

    inactive_result = db.execute(update(Jobs).where(Jobs.id.in_(select(SavedJobs.job_id))).where(Jobs.valid_until < now).where(Jobs.is_active == True).values(is_active=False))
    delete_result = db.execute(delete(Jobs).where(Jobs.id.not_in(select(SavedJobs.job_id))).where(Jobs.valid_until < now))
    accounts_deleted = db.execute(delete(User).where(User.is_verified == False,User.created_at < cutoff))
    db.commit()
    print("clean")
    return {"marked_inactive": inactive_result.rowcount,
            "jobs_deleted": delete_result.rowcount,
            "unverified_accounts_deleted": accounts_deleted.rowcount}