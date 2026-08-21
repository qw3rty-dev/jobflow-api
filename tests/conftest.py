import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models import User
from src.database import get_db
from src.security.password import hash_password
from tests.db import TestingSessionLocal,engine

@pytest.fixture
def override_get_db(db):
    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection, join_transaction_mode="create_savepoint")
    yield db
    db.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(override_get_db):
    return TestClient(app)

@pytest.fixture
def test_user(db):
    user = User(
        username ="testuser",
        email = "test@example.com",
        password_hash = hash_password("password")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



@pytest.fixture
def auth_headers(client,test_user):
    login = client.post(
        "/auth/login",
        data= {
            "username":test_user.email,
            "password":"password"
        }
    )
    token = login.json()["access_token"]
    return {"Authorization":f"Bearer {token}"}