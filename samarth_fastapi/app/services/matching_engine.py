"""
Matching Engine Service - Rule-based scoring model for internship recommendations.
TODO: Replace with ML-based matching in production.
"""
from typing import List, Dict, Any
from app.utils.helpers import INTERNSHIPS_DB, STUDENTS_DB
from app.schemas.internship_schema import InternshipResponse, RecommendationResponse


def calculate_match_score(
    internship: Dict[str, Any],
    student: Dict[str, Any]
) -> float:
    """
    Calculate a match score between a student and an internship.
    
    Scoring factors:
    1. Skill match (0-50 points)
    2. Location match (0-30 points)
    3. Interest match (0-20 points)
    
    Total: 0-100 points
    
    Args:
        internship: Internship dictionary
        student: Student dictionary
        
    Returns:
        Match score (0-100)
    """
    score = 0.0
    
    # 1. Skill Match (0-50 points)
    student_skills = set(skill.lower() for skill in student.get("skills", []))
    required_skills = set(skill.lower() for skill in internship.get("skills_required", []))
    
    if required_skills:
        matched_skills = student_skills.intersection(required_skills)
        skill_match_ratio = len(matched_skills) / len(required_skills)
        score += skill_match_ratio * 50
    
    # 2. Location Match (0-30 points)
    student_location = student.get("location", "").lower()
    internship_location = internship.get("location", "").lower()
    
    if student_location and internship_location:
        if student_location == internship_location:
            score += 30
        elif student_location in internship_location or internship_location in student_location:
            score += 15
    
    # 3. Interest Match (0-20 points)
    # Check if internship title/description contains keywords from student interests
    student_interests = set(interest.lower() for interest in student.get("interests", []))
    internship_text = (
        internship.get("title", "").lower() + " " + 
        internship.get("description", "").lower()
    )
    
    if student_interests:
        matched_interests = sum(
            1 for interest in student_interests 
            if interest in internship_text
        )
        interest_match_ratio = matched_interests / len(student_interests)
        score += interest_match_ratio * 20
    
    return round(score, 2)


def get_recommendations(
    student_id: int,
    limit: int = 10
) -> List[RecommendationResponse]:
    """
    Get personalized internship recommendations for a student.
    
    Args:
        student_id: ID of the student
        limit: Maximum number of recommendations to return
        
    Returns:
        List of recommendations sorted by score (highest first)
    """
    student = STUDENTS_DB.get(student_id)
    if not student:
        return []
    
    recommendations = []
    
    # Calculate scores for all internships
    for internship_id, internship in INTERNSHIPS_DB.items():
        score = calculate_match_score(internship, student)
        
        # Determine if student can apply
        # Apply button logic: if source == "admin" → apply=true, if source == "scraper" → apply=false
        can_apply = internship.get("source") == "admin"
        
        # Convert internship dict to InternshipResponse
        internship_response = InternshipResponse(
            id=internship["id"],
            title=internship["title"],
            description=internship["description"],
            skills_required=internship["skills_required"],
            location=internship["location"],
            source=internship["source"],
            admin_can_apply=internship["admin_can_apply"],
            apply_url=internship.get("apply_url"),
            created_at=internship["created_at"]
        )
        
        recommendations.append(
            RecommendationResponse(
                internship=internship_response,
                score=score,
                can_apply=can_apply
            )
        )
    
    # Sort by score (highest first) and return top N
    recommendations.sort(key=lambda x: x.score, reverse=True)
    return recommendations[:limit]
