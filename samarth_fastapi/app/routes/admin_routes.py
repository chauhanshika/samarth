"""
Admin routes for login, dashboard, managing internships, applications, and allocations.
"""
from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional, List
from app.schemas.admin_schema import AdminLogin, AdminResponse, AdminSummary
from app.schemas.internship_schema import InternshipCreate, InternshipResponse
from app.schemas.application_schema import ApplicationResponse, AllocationResponse, AllocationCreate
from app.utils.helpers import (
    ADMINS_DB,
    INTERNSHIPS_DB,
    APPLICATIONS_DB,
    ALLOCATIONS_DB,
    STUDENTS_DB,
    get_next_id,
    create_token,
    verify_token
)
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_current_admin(authorization: Optional[str] = Header(None)):
    """Dependency to get current authenticated admin."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    user_info = verify_token(token)
    
    if not user_info or user_info.get("user_type") != "admin":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    admin_id = user_info.get("user_id")
    admin = ADMINS_DB.get(admin_id)
    
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return admin


@router.post("/login", response_model=AdminResponse)
async def login_admin(credentials: AdminLogin):
    """
    Login as admin.
    """
    # Find admin by email
    admin = None
    for a in ADMINS_DB.values():
        if a["email"] == credentials.email:
            admin = a
            break
    
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check password (TODO: Use hashed passwords in production)
    if admin["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate token
    token = create_token(admin["id"], "admin", admin["email"])
    
    return AdminResponse(
        admin_id=admin["id"],
        email=admin["email"],
        token=token
    )


@router.get("/summary", response_model=AdminSummary)
async def get_summary(current_admin: dict = Depends(get_current_admin)):
    """
    Get admin dashboard summary with total submissions, allocations, and interns.
    """
    total_submissions = len(APPLICATIONS_DB)
    total_allocations = len(ALLOCATIONS_DB)
    
    # Count unique students who have been allocated
    allocated_student_ids = set(
        allocation["student_id"] for allocation in ALLOCATIONS_DB.values()
    )
    total_interns = len(allocated_student_ids)
    
    # Count pending applications
    pending_applications = sum(
        1 for app in APPLICATIONS_DB.values() 
        if app["status"] == "pending"
    )
    
    return AdminSummary(
        total_submissions=total_submissions,
        total_allocations=total_allocations,
        total_interns=total_interns,
        pending_applications=pending_applications
    )


@router.post("/internships/add", response_model=InternshipResponse, status_code=201)
async def add_internship(
    internship_data: InternshipCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Manually add a new internship (admin-only).
    """
    internship_id = get_next_id(INTERNSHIPS_DB)
    
    new_internship = {
        "id": internship_id,
        "title": internship_data.title,
        "description": internship_data.description,
        "skills_required": internship_data.skills_required,
        "location": internship_data.location,
        "source": "admin",  # Admin-added internships
        "apply_url": internship_data.apply_url,
        "admin_can_apply": True,  # Admin-added internships can be applied to
        "created_at": datetime.now()
    }
    
    INTERNSHIPS_DB[internship_id] = new_internship
    
    return InternshipResponse(**new_internship)


@router.get("/internships", response_model=List[InternshipResponse])
async def get_all_internships(current_admin: dict = Depends(get_current_admin)):
    """
    View all internships (both scraper and admin-added).
    """
    internships = []
    for internship in INTERNSHIPS_DB.values():
        internships.append(InternshipResponse(**internship))
    
    return internships


@router.get("/applications", response_model=List[ApplicationResponse])
async def get_all_applications(current_admin: dict = Depends(get_current_admin)):
    """
    View all applications.
    """
    applications = []
    for application in APPLICATIONS_DB.values():
        applications.append(ApplicationResponse(**application))
    
    return applications


@router.post("/allocate/{application_id}", response_model=AllocationResponse, status_code=201)
async def allocate_internship(
    application_id: int,
    allocation_data: Optional[AllocationCreate] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Allocate an internship to a student (approve their application).
    """
    # Check if application exists
    application = APPLICATIONS_DB.get(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check if already allocated
    for allocation in ALLOCATIONS_DB.values():
        if allocation["application_id"] == application_id:
            raise HTTPException(status_code=400, detail="Application already allocated")
    
    # Get internship details
    internship = INTERNSHIPS_DB.get(application["internship_id"])
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    # Create allocation
    allocation_id = get_next_id(ALLOCATIONS_DB)
    new_allocation = {
        "id": allocation_id,
        "application_id": application_id,
        "student_id": application["student_id"],
        "student_name": application["student_name"],
        "internship_id": application["internship_id"],
        "internship_title": application["internship_title"],
        "status": "allocated",
        "allocated_at": datetime.now()
    }
    
    ALLOCATIONS_DB[allocation_id] = new_allocation
    
    # Update application status
    application["status"] = "allocated"
    
    return AllocationResponse(**new_allocation)
