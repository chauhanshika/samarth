"""
Student routes for registration, login, profile, search, recommendations, and applications.
"""
from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List,Optional

from app.schemas.student_schema import (
    StudentRegister,
    StudentLogin,
    StudentProfile,
    StudentProfileUpdate,
    StudentResponse
)
from app.schemas.internship_schema import (
    InternshipResponse,
    InternshipSearchParams,
    RecommendationRequest,
    RecommendationResponse
)
from app.schemas.application_schema import ApplicationResponse
from app.utils.helpers import (
    STUDENTS_DB,
    APPLICATIONS_DB,
    get_next_id,
    create_token,
    verify_token,
    INTERNSHIPS_DB
)
from app.services.matching_engine import get_recommendations
from datetime import datetime

router = APIRouter(prefix="/student", tags=["Student"])


def get_current_student(authorization: Optional[str] = Header(None)):
    """Dependency to get current authenticated student."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    user_info = verify_token(token)
    
    if not user_info or user_info.get("user_type") != "student":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    student_id = user_info.get("user_id")
    student = STUDENTS_DB.get(student_id)
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student


@router.post("/register", response_model=StudentResponse, status_code=201)
async def register_student(student_data: StudentRegister):
    """
    Register a new student.
    """
    # Check if email already exists
    for student in STUDENTS_DB.values():
        if student["email"] == student_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new student
    student_id = get_next_id(STUDENTS_DB)
    new_student = {
        "id": student_id,
        "email": student_data.email,
        "password": student_data.password,  # TODO: Hash password in production
        "full_name": student_data.full_name,
        "phone": student_data.phone,
        "skills": student_data.skills or [],
        "interests": student_data.interests or [],
        "location": student_data.location,
        "created_at": datetime.now()
    }
    
    STUDENTS_DB[student_id] = new_student
    
    # Generate token
    token = create_token(student_id, "student", student_data.email)
    
    return StudentResponse(
        student_id=student_id,
        email=student_data.email,
        full_name=student_data.full_name,
        token=token
    )


@router.post("/login", response_model=StudentResponse)
async def login_student(credentials: StudentLogin):
    """
    Login a student.
    """
    # Find student by email
    student = None
    for s in STUDENTS_DB.values():
        if s["email"] == credentials.email:
            student = s
            break
    
    if not student:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check password (TODO: Use hashed passwords in production)
    if student["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate token
    token = create_token(student["id"], "student", student["email"])
    
    return StudentResponse(
        student_id=student["id"],
        email=student["email"],
        full_name=student["full_name"],
        token=token
    )


@router.get("/profile", response_model=StudentProfile)
async def get_profile(current_student: dict = Depends(get_current_student)):
    """
    Get current student's profile.
    """
    return StudentProfile(
        id=current_student["id"],
        email=current_student["email"],
        full_name=current_student["full_name"],
        phone=current_student.get("phone"),
        skills=current_student.get("skills", []),
        interests=current_student.get("interests", []),
        location=current_student.get("location"),
        created_at=current_student["created_at"]
    )


@router.put("/profile/update", response_model=StudentProfile)
async def update_profile(
    profile_update: StudentProfileUpdate,
    current_student: dict = Depends(get_current_student)
):
    """
    Update current student's profile.
    """
    # Update fields if provided
    if profile_update.full_name is not None:
        current_student["full_name"] = profile_update.full_name
    if profile_update.phone is not None:
        current_student["phone"] = profile_update.phone
    if profile_update.skills is not None:
        current_student["skills"] = profile_update.skills
    if profile_update.interests is not None:
        current_student["interests"] = profile_update.interests
    if profile_update.location is not None:
        current_student["location"] = profile_update.location
    
    return StudentProfile(
        id=current_student["id"],
        email=current_student["email"],
        full_name=current_student["full_name"],
        phone=current_student.get("phone"),
        skills=current_student.get("skills", []),
        interests=current_student.get("interests", []),
        location=current_student.get("location"),
        created_at=current_student["created_at"]
    )


@router.get("/internships/search", response_model=List[InternshipResponse])
async def search_internships(
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    skills: Optional[str] = None
):
    """
    Search internships by keyword, location, or skills.
    Skills should be comma-separated.
    """
    results = []
    skills_list = [s.strip() for s in skills.split(",")] if skills else []
    
    for internship in INTERNSHIPS_DB.values():
        # Keyword search
        if keyword:
            keyword_lower = keyword.lower()
            if (keyword_lower not in internship["title"].lower() and 
                keyword_lower not in internship["description"].lower()):
                continue
        
        # Location search
        if location:
            if location.lower() not in internship["location"].lower():
                continue
        
        # Skills search
        if skills_list:
            internship_skills = [s.lower() for s in internship["skills_required"]]
            if not any(skill.lower() in internship_skills for skill in skills_list):
                continue
        
        results.append(InternshipResponse(
            id=internship["id"],
            title=internship["title"],
            description=internship["description"],
            skills_required=internship["skills_required"],
            location=internship["location"],
            source=internship["source"],
            admin_can_apply=internship["admin_can_apply"],
            apply_url=internship.get("apply_url"),
            created_at=internship["created_at"]
        ))
    
    return results


@router.post("/recommend", response_model=List[RecommendationResponse])
async def get_recommendations_endpoint(
    request: Optional[RecommendationRequest] = None,
    current_student: dict = Depends(get_current_student)
):
    """
    Get personalized internship recommendations for the current student.
    """
    # Use current student's ID from token
    limit = request.limit if request and request.limit else 10
    recommendations = get_recommendations(
        student_id=current_student["id"],
        limit=limit
    )
    
    return recommendations


@router.post("/apply/{internship_id}", response_model=ApplicationResponse, status_code=201)
async def apply_for_internship(
    internship_id: int,
    current_student: dict = Depends(get_current_student)
):
    """
    Apply for an internship. Only allowed for admin-added internships.
    """
    # Check if internship exists
    internship = INTERNSHIPS_DB.get(internship_id)
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    # Apply button logic: Only admin-added internships can be applied to
    if internship.get("source") != "admin":
        raise HTTPException(
            status_code=400,
            detail="Cannot apply to scraper-added internships. Only admin-added internships can be applied to."
        )
    
    # Check if already applied
    for application in APPLICATIONS_DB.values():
        if (application["student_id"] == current_student["id"] and 
            application["internship_id"] == internship_id):
            raise HTTPException(status_code=400, detail="Already applied for this internship")
    
    # Create application
    application_id = get_next_id(APPLICATIONS_DB)
    new_application = {
        "id": application_id,
        "student_id": current_student["id"],
        "student_name": current_student["full_name"],
        "student_email": current_student["email"],
        "internship_id": internship_id,
        "internship_title": internship["title"],
        "status": "pending",
        "applied_at": datetime.now()
    }
    
    APPLICATIONS_DB[application_id] = new_application
    
    return ApplicationResponse(**new_application)
