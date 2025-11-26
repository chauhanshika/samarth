"""
SAMARTH FastAPI Backend - Main Application Entry Point

This is a complete FastAPI backend for the SAMARTH project.
It supports two user types: Students (Appliers) and Government Admins.

Features:
- Student registration, login, profile management
- Internship search and recommendations
- Application system (only for admin-added internships)
- Admin dashboard and internship management
- Allocation system for approved applications
- Rule-based matching engine for recommendations

TODO: 
- Replace dummy data storage with actual database (SQLAlchemy/PostgreSQL)
- Add password hashing (bcrypt)
- Add JWT token authentication
- Integrate with scraper service
- Replace rule-based matching with ML model
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import student_routes, admin_routes, internship_routes

# Initialize FastAPI app
app = FastAPI(
    title="SAMARTH Backend API",
    description="FastAPI backend for SAMARTH internship platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(student_routes.router)
app.include_router(admin_routes.router)
app.include_router(internship_routes.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to SAMARTH Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from app.routes import admin_scraper_route

app.include_router(admin_scraper_route.router, prefix="/api")
