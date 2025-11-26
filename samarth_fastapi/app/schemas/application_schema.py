"""
Application and allocation-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ApplicationResponse(BaseModel):
    """Schema for application response."""
    id: int
    student_id: int
    student_name: str
    student_email: str
    internship_id: int
    internship_title: str
    status: str  # "pending", "approved", "rejected", "allocated"
    applied_at: datetime

    class Config:
        from_attributes = True


class AllocationResponse(BaseModel):
    """Schema for allocation response."""
    id: int
    application_id: int
    student_id: int
    student_name: str
    internship_id: int
    internship_title: str
    status: str  # "allocated", "completed", "cancelled"
    allocated_at: datetime

    class Config:
        from_attributes = True


class AllocationCreate(BaseModel):
    """Schema for creating an allocation."""
    application_id: int
    notes: Optional[str] = None
