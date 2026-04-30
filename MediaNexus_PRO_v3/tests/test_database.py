import pytest
from core.database import DatabaseManager
from pathlib import Path
import os

@pytest.fixture
def db():
    db_path = Path("test_medianexus.db")
    if db_path.exists():
        os.remove(db_path)
    manager = DatabaseManager(db_path)
    yield manager
    if db_path.exists():
        os.remove(db_path)

def test_profile_creation_and_hashing(db):
    profile_id = db.create_profile("Test User", password="securepassword123")
    assert profile_id is not None
    
    # Verify correct password
    assert db.verify_password(profile_id, "securepassword123") is True
    
    # Verify incorrect password
    assert db.verify_password(profile_id, "wrongpassword") is False

def test_profile_no_password(db):
    profile_id = db.create_profile("No Pass User")
    assert db.verify_password(profile_id, "") is True
    assert db.verify_password(profile_id, "something") is False
