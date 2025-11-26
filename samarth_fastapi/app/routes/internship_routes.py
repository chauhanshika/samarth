"""
General internship routes (if needed for shared functionality).
Currently, internships are handled in student_routes and admin_routes.
This file is kept for future extensibility.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/internships", tags=["Internships"])

# This router can be used for public internship endpoints if needed
# For now, internships are accessed through student and admin routes
