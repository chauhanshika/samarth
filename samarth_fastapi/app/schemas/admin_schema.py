"""
Admin-related Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr


class AdminLogin(BaseModel):
    """Schema for admin login."""
    email: EmailStr
    password: str


class AdminResponse(BaseModel):
    """Schema for admin login response."""
    admin_id: int
    email: str
    token: str


class AdminSummary(BaseModel):
    """Schema for admin dashboard summary."""
    total_submissions: int
    total_allocations: int
    total_interns: int
    pending_applications: int
