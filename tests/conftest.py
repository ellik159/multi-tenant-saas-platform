import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from src.main import app
from src.database.session import Base, get_db
from src.core.config import settings

# Test database URL - use environment variable or derive from settings
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    settings.DATABASE_URL.replace("/saas_db", "/saas_test_db")
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for each test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_credentials():
    """Test user credentials"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "organization_name": "Test Org",
        "organization_slug": "test-org"
    }


@pytest.fixture
def get_auth_headers(client, test_user_credentials):
    """Helper to get authentication headers for testing"""
    def _get_headers():
        # Register and login to get token
        response = client.post("/api/v1/auth/register", json=test_user_credentials)
        if response.status_code == 201:
            token = response.json()["access_token"]
        else:
            # Try login if already registered
            login_data = {
                "email": test_user_credentials["email"],
                "password": test_user_credentials["password"]
            }
            response = client.post("/api/v1/auth/login", json=login_data)
            token = response.json()["access_token"]
        
        return {"Authorization": f"Bearer {token}"}
    
    return _get_headers
