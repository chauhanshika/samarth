"""
Student-related Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class StudentRegister(BaseModel):
    """Schema for student registration."""
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    skills: List[str] = []
    interests: List[str] = []
    location: Optional[str] = None


class StudentLogin(BaseModel):
    """Schema for student login."""
    email: EmailStr
    password: str


class StudentProfile(BaseModel):
    """Schema for student profile response."""
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    skills: List[str]
    interests: List[str]
    location: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StudentProfileUpdate(BaseModel):
    """Schema for updating student profile."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    location: Optional[str] = None


class StudentResponse(BaseModel):
    """Schema for student response with token."""
    student_id: int
    email: str
    full_name: str
    token: str
