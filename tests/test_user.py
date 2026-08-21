from src.models import SavedJobs,Jobs


def test_get_saved_jobs(client,test_user,db,auth_headers):
    test_user.is_verified = True
    db.commit()
    
    response = client.get("/user/",
                          headers=auth_headers
                          )

    assert response.status_code == 200
    assert isinstance(response.json(),list)

def test_get_saved_jobs_unverified(client,test_user,auth_headers):


    response = client.get("/user/",
                          headers=auth_headers
                          )

    assert response.status_code == 403

def test_get_saved_jobs_no_auth(client):
    response = client.get("/user/")
    assert response.status_code == 401


def test_get_saved_jobs_empty(client,test_user,db,auth_headers):
    test_user.is_verified = True
    db.commit()

    response = client.get("/user/",
                          headers=auth_headers
                          )

    assert response.status_code == 200
    assert response.json() == []



def test_get_saved_jobs(test_user,client,db,auth_headers):
    test_user.is_verified = True
    job = Jobs(
        title="Backend Developer",
        company="Test Company",
        location="Remote",
        link="https://example.com/job/1",
        source="test"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    saved_job = SavedJobs(
        user_id=test_user.id,
        job_id=job.id
    )
    db.add(saved_job)
    db.commit()

    response = client.get("/user/",
                          headers=auth_headers
                          )

    assert response.status_code == 200
    assert response.json() != []


def test_get_saved_job(test_user,client,db,auth_headers):
    test_user.is_verified = True
    job = Jobs(
        title="Backend Developer",
        company="Test Company",
        location="Remote",
        link="https://example.com/job/1",
        source="test"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    saved_job = SavedJobs(
        user_id=test_user.id,
        job_id=job.id
    )
    db.add(saved_job)
    db.commit()


    response = client.get("/user/",
                          headers=auth_headers
                          )
    assert response.status_code == 200
    assert response.json()[0]['job']['id']== job.id
    

def test_delete_saved_job(test_user,client,db,auth_headers):
    test_user.is_verified = True
    job = Jobs(
        title="Backend Developer",
        company="Test Company",
        location="Remote",
        link="https://example.com/job/1",
        source="test"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    saved_job = SavedJobs(
        user_id=test_user.id,
        job_id=job.id
    )
    db.add(saved_job)
    db.commit()
    db.refresh(saved_job)


    delete = client.delete(f"/user/remove/{saved_job.id}",
                          headers=auth_headers)
    
    assert delete.status_code == 204
    deleted = db.get(SavedJobs,saved_job.id)
    assert deleted is None



def test_edit_savedjob(db,test_user,client,auth_headers):

    test_user.is_verified = True
    job = Jobs(
        title="Backend Developer",
        company="Test Company",
        location="Remote",
        link="https://example.com/job/1",
        source="test"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    saved_job = SavedJobs(
        user_id=test_user.id,
        job_id=job.id
    )
    db.add(saved_job)
    db.commit()

    response = client.patch(
        f"/user/edit/{saved_job.id}",
        json={
            "notes": "test_notes"

        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["notes"] == "test_notes"