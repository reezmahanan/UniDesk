import pytest
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Configure test environment
os.environ["DATABASE_URL"] = "sqlite:///./test_apex.db"
os.environ["MOCK_AI_MODE"] = "true"

from app.database import Base, get_db
from app.main import app
from app.seed import init_db_data
from app.core.rate_limit import rate_limiter

TEST_DATABASE_URL = "sqlite:///./test_apex.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(autouse=True)
def clear_rate_limits(client):
    rate_limiter.reset()
    client.cookies.clear()

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    init_db_data()
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_apex.db"):
        try:
            os.remove("./test_apex.db")
        except Exception:
            pass

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def student_auth_headers(client):
    res = client.post("/api/auth/login", json={"email": "student@apex.edu.lk", "password": "student123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def student2_auth_headers(client):
    res = client.post("/api/auth/login", json={"email": "sanduni@apex.edu.lk", "password": "student123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def staff_auth_headers(client):
    res = client.post("/api/auth/login", json={"email": "staff@apex.edu.lk", "password": "staff123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_auth_headers(client):
    res = client.post("/api/auth/login", json={"email": "admin@apex.edu.lk", "password": "admin123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
