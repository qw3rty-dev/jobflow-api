from src.models import User
from sqlalchemy import select

def test_register(client,db):
    response = client.post(
        "/auth/register",
        json={
            "username": "new_user",
            "email": "new@example.com",
            "password": "password"
        }
    )
    assert response.status_code == 201
    user = db.scalar(select(User).where(User.email == "new@example.com"))

    assert user is not None



def test_register_existing_email(client,test_user):
    response = client.post(
        "/auth/register",
        json={
            "username": test_user.username,
            "email": test_user.email,
            "password": "password"
        }
    )
    assert response.status_code == 409


def test_login(client,test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": "password"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client,test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": "wrong_password"
        }
    )
    assert response.status_code == 401

    assert response.json()["detail"] == "Invalid credentials"
    

def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "nonexistent_user@example.com",
            "password": "password"
        }
    )
    assert response.status_code == 401
 
    assert response.json()["detail"] == "Invalid credentials"