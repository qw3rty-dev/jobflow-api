from src.models import Jobs
from sqlalchemy import select

def test_get_jobs(db,client):
        
    job1 = Jobs(
    title="Backend Developer",
    company="Test Company",
    location="Remote",
    link="https://example.com/job/1",
    source="test"
    )

    job2 = Jobs(
    title="Frontend Developer",
    company="Fake Company",
    location="Remote",
    link="https://example.com/job/2",
    source="test"
    )
    job3 = Jobs(
    title="Backend Engineer",
    company="La la land",
    location="Remote",
    link="https://example.com/job/3",
    source="test"
    )
    db.add_all([job1,job2,job3])
    db.commit()

    response = client.get("/jobs?keyword=backend")

    assert response.status_code== 200
    assert all(job["title"] != "Frontend Developer" for job in response.json()["jobs"])

def test_get_jobs_pagination(db,client):
        
    job1 = Jobs(
    title="Backend Developer",
    company="Test Company",
    location="Remote",
    link="https://example.com/job/1",
    source="test"
    )

    job2 = Jobs(
    title="Frontend Developer",
    company="Fake Company",
    location="Remote",
    link="https://example.com/job/2",
    source="test"
    )
    job3 = Jobs(
    title="Backend Engineer",
    company="La la land",
    location="Remote",
    link="https://example.com/job/3",
    source="test"
    )
    db.add_all([job1,job2,job3])
    db.commit()

    response = client.get("/jobs?limit=2&page=1")

    assert response.status_code== 200
    assert response.json()["meta"]["total"] == 3
    assert response.json()["meta"]["total_pages"] == 2
    assert len(response.json()["jobs"]) == 2


def test_get_job_by_id(db,client):
    job = Jobs(
        title="testjob",
        company="jobflow",
        location="remote",
        link="https://example.com",
        source="test"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    response = client.get(f"/jobs/{job.id}")
    assert response.status_code == 200
    assert response.json()["id"] == job.id
    assert response.json()["title"] == job.title


def test_get_job_by_non_existent_id(client):
    response = client.get("/jobs/999999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
    