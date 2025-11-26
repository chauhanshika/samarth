"""
Helper utilities for the SAMARTH backend.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import secrets


# Dummy data storage (in-memory)
# TODO: Replace with actual database connections

# Students storage
STUDENTS_DB: Dict[int, Dict[str, Any]] = {}

# Admins storage
ADMINS_DB: Dict[int, Dict[str, Any]] = {
    1: {
        "id": 1,
        "email": "admin@samarth.gov",
        "password": "admin123",  # In production, use hashed passwords
        "full_name": "Government Admin",
        "created_at": datetime.now()
    }
}

# Internships storage
INTERNSHIPS_DB: Dict[int, Dict[str, Any]] = {}

# Applications storage
APPLICATIONS_DB: Dict[int, Dict[str, Any]] = {}

# Allocations storage
ALLOCATIONS_DB: Dict[int, Dict[str, Any]] = {}

# Token storage (for authentication)
TOKEN_STORAGE: Dict[str, Dict[str, Any]] = {}


def generate_token() -> str:
    """Generate a random token for authentication."""
    return secrets.token_urlsafe(32)


def get_next_id(collection: Dict[int, Any]) -> int:
    """Get the next available ID for a collection."""
    if not collection:
        return 1
    return max(collection.keys()) + 1


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a token and return user info."""
    return TOKEN_STORAGE.get(token)


def create_token(user_id: int, user_type: str, email: str) -> str:
    """Create and store a token for a user."""
    token = generate_token()
    TOKEN_STORAGE[token] = {
        "user_id": user_id,
        "user_type": user_type,  # "student" or "admin"
        "email": email
    }
    return token


# Initialize with some dummy data
def initialize_dummy_data():
    """Initialize the database with dummy data for testing."""
    global INTERNSHIPS_DB, STUDENTS_DB
    
    # Add some dummy internships (mix of scraper and admin)
    scraper_internships = [
        {
            "id": 1,
            "title": "Software Development Intern",
            "description": "Work on cutting-edge web applications using Python and FastAPI.",
            "skills_required": ["Python", "FastAPI", "REST API"],
            "location": "Delhi",
            "source": "scraper",
            "apply_url": "https://example.com/apply/1",
            "admin_can_apply": False,
            "created_at": datetime.now()
        },
        {
            "id": 2,
            "title": "Data Science Intern",
            "description": "Analyze large datasets and build ML models.",
            "skills_required": ["Python", "Machine Learning", "Data Analysis"],
            "location": "Bangalore",
            "source": "scraper",
            "apply_url": "https://example.com/apply/2",
            "admin_can_apply": False,
            "created_at": datetime.now()
        },
        {
            "id": 3,
            "title": "Frontend Developer Intern",
            "description": "Build responsive user interfaces with React.",
            "skills_required": ["React", "JavaScript", "CSS"],
            "location": "Mumbai",
            "source": "scraper",
            "apply_url": "https://example.com/apply/3",
            "admin_can_apply": False,
            "created_at": datetime.now()
        }
    ]
    
    admin_internships = [
        {
            "id": 4,
            "title": "Government Digital Services Intern",
            "description": "Help digitize government services and improve citizen experience.",
            "skills_required": ["Python", "Database", "API Development"],
            "location": "Delhi",
            "source": "admin",
            "apply_url": None,
            "admin_can_apply": True,
            "created_at": datetime.now()
        },
        {
            "id": 5,
            "title": "Public Policy Research Intern",
            "description": "Research and analyze policy impacts on citizens.",
            "skills_required": ["Research", "Analysis", "Writing"],
            "location": "Delhi",
            "source": "admin",
            "apply_url": None,
            "admin_can_apply": True,
            "created_at": datetime.now()
        }
    ]
    
    for internship in scraper_internships + admin_internships:
        INTERNSHIPS_DB[internship["id"]] = internship


# Initialize dummy data on import
initialize_dummy_data()
