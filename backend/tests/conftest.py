import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.kit import Kit  # Import models to ensure they're registered

# Use a test database file that we clean up
TEST_DATABASE_URL = "sqlite:///./test_custody_manager.db"


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Remove the test database if it exists
    if os.path.exists("test_custody_manager.db"):
        os.remove("test_custody_manager.db")
    
    # Create a new engine for this test
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
        # Clean up the test database file
        if os.path.exists("test_custody_manager.db"):
            os.remove("test_custody_manager.db")


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
