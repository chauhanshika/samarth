"""
Internship-related Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class InternshipBase(BaseModel):
    """Base schema for internship."""
    title: str
    description: str
    skills_required: List[str]
    location: str
    apply_url: Optional[str] = None


class InternshipCreate(InternshipBase):
    """Schema for creating an internship (admin only)."""
    pass


class InternshipResponse(InternshipBase):
    """Schema for internship response."""
    id: int
    source: str  # "scraper" or "admin"
    admin_can_apply: bool  # True if source == "admin", False if source == "scraper"
    created_at: datetime

    class Config:
        from_attributes = True


class InternshipSearchParams(BaseModel):
    """Schema for internship search parameters."""
    keyword: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None


class RecommendationRequest(BaseModel):
    """Schema for recommendation request."""
    limit: Optional[int] = 10


class RecommendationResponse(BaseModel):
    """Schema for recommendation response."""
    internship: InternshipResponse
    score: float
    can_apply: bool  # True if source == "admin", False if source == "scraper"
