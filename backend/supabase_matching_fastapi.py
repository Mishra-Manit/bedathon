#!/usr/bin/env python3
"""
FastAPI endpoints for Supabase-integrated roommate matching system
Uses existing Profile and ApartmentComplex models from Supabase database
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
import json
from supabase_roommate_matcher import SupabaseRoommateMatcher
from models import Profile, ProfileCreate, ProfileRead
from sqlmodel import Session, create_engine, select
import os
from dotenv import load_dotenv

load_dotenv()

# Create router for matching endpoints
matching_router = APIRouter(prefix="/matching", tags=["matching"])

def calculate_compatibility(user_prefs: Dict[str, Any], profile: Dict[str, Any]) -> float:
    """Calculate compatibility using statistical distance (lower distance = higher compatibility)"""
    import math
    
    # Convert preference strings to numbers (1-5 scale)
    def pref_to_number(pref_str) -> int:
        if pref_str is None:
            return 3  # Default to MEDIUM if None
        pref_map = {
            "VERY_LOW": 1,
            "LOW": 2, 
            "MEDIUM": 3,
            "HIGH": 4,
            "VERY_HIGH": 5
        }
        return pref_map.get(str(pref_str).upper(), 3)
    
    # Convert user preferences to numerical values (handle None values)
    user_cleanliness = pref_to_number(user_prefs.get("cleanliness"))
    user_noise = pref_to_number(user_prefs.get("noise_level"))
    user_study = pref_to_number(user_prefs.get("study_time"))
    user_social = pref_to_number(user_prefs.get("social_level"))
    user_sleep = pref_to_number(user_prefs.get("sleep_schedule"))
    
    # Get profile numerical values
    profile_cleanliness = profile["cleanliness"]
    profile_noise = profile["noise"]
    profile_study = profile["study_time"]
    profile_social = profile["social"]
    profile_sleep = profile["sleep"]
    
    # Create preference vectors
    user_vector = [user_cleanliness, user_noise, user_study, user_social, user_sleep]
    profile_vector = [profile_cleanliness, profile_noise, profile_study, profile_social, profile_sleep]
    
    # Calculate Euclidean distance between preference vectors
    distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(user_vector, profile_vector)))
    
    # Convert distance to compatibility score (0-1 scale)
    # Maximum possible distance is sqrt(5 * 4^2) = sqrt(80) ≈ 8.94
    max_distance = math.sqrt(5 * 16)  # sqrt(80) ≈ 8.94
    base_compatibility = max(0.05, 1.0 - (distance / max_distance))
    
    # Add budget compatibility bonus (handle None values)
    budget_min = user_prefs.get("budget_min") or 800
    budget_max = user_prefs.get("budget_max") or 1200
    user_budget_avg = (budget_min + budget_max) / 2
    profile_budget = profile["budget"]
    budget_diff = abs(user_budget_avg - profile_budget)
    budget_bonus = max(0, 0.15 - budget_diff / 1000.0)  # Up to 15% bonus for budget match
    
    # Add categorical bonuses (handle None values)
    user_year = (user_prefs.get("year") or "Junior").lower()
    user_major = (user_prefs.get("major") or "Computer Science").lower()
    year_bonus = 0.1 if user_year == profile["year"].lower() else 0
    major_bonus = 0.15 if user_major == profile["major"].lower() else 0
    
    final_score = base_compatibility + budget_bonus + year_bonus + major_bonus
    
    print(f"🔍 STATS: {profile['name']} - Distance: {distance:.2f}, Base: {base_compatibility:.2f}, Budget: +{budget_bonus:.2f}, Year: +{year_bonus:.2f}, Major: +{major_bonus:.2f} = {final_score:.2f}")
    
    return max(0.05, min(1.0, final_score))

# Initialize the Supabase matcher
matcher = SupabaseRoommateMatcher()

# Database connection - use Supabase PostgreSQL if available, otherwise fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Try to construct Supabase PostgreSQL URL if we have the service role key
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if supabase_url and supabase_service_key:
        # Extract the project ref from the Supabase URL
        project_ref = supabase_url.split("//")[1].split(".")[0]
        # Use the service role key as password for direct PostgreSQL connection
        DATABASE_URL = f"postgresql://postgres:{supabase_service_key}@db.{project_ref}.supabase.co:5432/postgres"
    else:
        DATABASE_URL = "sqlite:///./bedathon.db"

engine = create_engine(DATABASE_URL)

class RoommatePreferencesRequest(BaseModel):
    name: str
    email: str
    budget_min: int = Field(ge=0, description="Minimum budget")
    budget_max: int = Field(ge=0, description="Maximum budget")
    preferred_bedrooms: int = Field(ge=1, le=5, description="Preferred number of bedrooms")
    cleanliness: str = Field(default="MEDIUM", description="Cleanliness preference: VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH")
    noise_level: str = Field(default="MEDIUM", description="Noise level preference: VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH")
    study_time: str = Field(default="MEDIUM", description="Study time preference: VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH")
    social_level: str = Field(default="MEDIUM", description="Social level preference: VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH")
    sleep_schedule: str = Field(default="MEDIUM", description="Sleep schedule preference: VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH")
    pet_friendly: bool = Field(default=False, description="Pet friendly preference")
    smoking: bool = Field(default=False, description="Smoking preference")
    year: str = Field(default="Junior", description="Academic year")
    major: str = Field(default="Computer Science", description="Major")

class RoommateMatchRequest(BaseModel):
    min_compatibility: float = Field(default=0.05, ge=0.0, le=1.0, description="Minimum compatibility score")
    # User profile fields
    name: Optional[str] = None
    email: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    preferred_bedrooms: Optional[int] = None
    cleanliness: Optional[str] = None
    noise_level: Optional[str] = None
    study_time: Optional[str] = None
    social_level: Optional[str] = None
    sleep_schedule: Optional[str] = None
    pet_friendly: Optional[bool] = None
    smoking: Optional[bool] = None
    year: Optional[str] = None
    major: Optional[str] = None

class ProfileResponse(BaseModel):
    id: str
    name: str
    year: str
    major: Optional[str]
    budget: int
    cleanliness: int
    noise_level: int
    study_time: int
    social_level: int
    sleep_schedule: int
    tags: List[str]
    created_at: str

class RoommateMatchResponse(BaseModel):
    roommate1: ProfileResponse
    roommate2: ProfileResponse
    compatibility_score: float
    compatibility_percentage: float

class ApartmentMatchResponse(BaseModel):
    apartment_name: str
    apartment_address: str
    bedroom_count: int
    price: str
    distance_to_vt: float
    amenities: List[str]
    match_score: float
    match_percentage: float
    reasons: List[str]
    roommate_compatibility: float
    apartment_features: Dict[str, Any]

class DataSummaryResponse(BaseModel):
    apartments: Dict[str, Any]
    profiles: Dict[str, Any]

def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session

def convert_preference_string_to_int(preference_str: str) -> int:
    """Convert string preference to integer (1-5)"""
    preference_mapping = {
        'VERY_LOW': 1,
        'LOW': 2,
        'MEDIUM': 3,
        'HIGH': 4,
        'VERY_HIGH': 5
    }
    return preference_mapping.get(preference_str.upper(), 3)

@matching_router.post("/roommate-preferences", response_model=Dict[str, Any])
async def create_roommate_profile(request: RoommatePreferencesRequest):
    """Create a new roommate profile in Supabase database"""
    try:
        # Generate tags based on preferences
        tags = []
        if request.pet_friendly:
            tags.append('pets')
        if request.smoking:
            tags.append('smoking')
        
        # Create profile in database
        profile_data = ProfileCreate(
            name=request.name,
            year=request.year,
            major=request.major,
            budget=request.budget_min,
            move_in=None,
            tags=tags,
            cleanliness=convert_preference_string_to_int(request.cleanliness),
            noise=convert_preference_string_to_int(request.noise_level),
            study_time=convert_preference_string_to_int(request.study_time),
            social=convert_preference_string_to_int(request.social_level),
            sleep=convert_preference_string_to_int(request.sleep_schedule)
        )
        
        with Session(engine) as session:
            # Check if profile already exists by name
            existing_profile = session.exec(select(Profile).where(Profile.name == request.name)).first()
            if existing_profile:
                # Update existing profile
                existing_profile.year = request.year
                existing_profile.major = request.major
                existing_profile.budget = request.budget_min
                existing_profile.tags = tags
                existing_profile.cleanliness = convert_preference_string_to_int(request.cleanliness)
                existing_profile.noise = convert_preference_string_to_int(request.noise_level)
                existing_profile.study_time = convert_preference_string_to_int(request.study_time)
                existing_profile.social = convert_preference_string_to_int(request.social_level)
                existing_profile.sleep = convert_preference_string_to_int(request.sleep_schedule)
                
                session.add(existing_profile)
                session.commit()
                session.refresh(existing_profile)
                profile = existing_profile
                message = "Profile updated successfully"
            else:
                # Create new profile
                profile = Profile.model_validate(profile_data)
                session.add(profile)
                session.commit()
                session.refresh(profile)
                message = "Profile created successfully"
        
        return {
            "message": message,
            "profile": {
                "id": str(profile.id),
                "name": profile.name,
                "year": profile.year,
                "major": profile.major,
                "budget": profile.budget
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.get("/profiles", response_model=Dict[str, Any])
async def get_all_profiles():
    """Get all profiles from Supabase profiles table"""
    try:
        # Use the Supabase profiles connector to get profiles from your dashboard
        profiles = matcher.profiles_connector.get_profiles()
        
        return {
            "profiles": profiles,
            "count": len(profiles)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.get("/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile_by_id(profile_id: str):
    """Get a specific profile by ID"""
    try:
        profile = matcher.get_profile_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return ProfileResponse(
            id=str(profile.id),
            name=profile.name,
            year=profile.year,
            major=profile.major,
            budget=profile.budget,
            cleanliness=profile.cleanliness,
            noise_level=profile.noise,
            study_time=profile.study_time,
            social_level=profile.social,
            sleep_schedule=profile.sleep,
            tags=profile.tags or [],
            created_at=profile.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.post("/roommate-matches", response_model=Dict[str, Any])
async def find_roommate_matches(request: RoommateMatchRequest):
    """Find compatible roommate matches from Supabase database"""
    try:
        print(f"🔍 DEBUG: Finding matches with threshold {request.min_compatibility}")
        
        # Get profiles from Supabase
        profiles = matcher.profiles_connector.get_profiles()
        print(f"🔍 DEBUG: Got {len(profiles)} profiles from Supabase")
        
        # Create proper matching function based on user preferences
        matches = []
        user_preferences = request.dict()
        print(f"🔍 DEBUG: User preferences from request: {user_preferences}")
        
        for profile in profiles:
            # Calculate actual compatibility based on preferences
            compatibility = calculate_compatibility(user_preferences, profile)
            
            if compatibility >= request.min_compatibility:
                matches.append({
                    "id": profile["id"],
                    "name": profile["name"],
                    "compatibility_percentage": int(compatibility * 100),
                    "year": profile["year"],
                    "major": profile["major"],
                    "budget": profile["budget"],
                    "preferences": {
                        "cleanliness": profile["cleanliness"],
                        "noise_level": profile["noise"],
                        "study_time": profile["study_time"],
                        "social_level": profile["social"],
                        "sleep_schedule": profile["sleep"]
                    }
                })
        
        # Sort by compatibility score (highest first)
        matches.sort(key=lambda x: x["compatibility_percentage"], reverse=True)
        
        print(f"🔍 DEBUG: Found {len(matches)} matches")
        return {
            "matches": matches,
            "count": len(matches),
            "min_compatibility": request.min_compatibility
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.get("/apartment-matches/{profile_id}", response_model=Dict[str, Any])
async def find_apartment_matches(profile_id: str, limit: int = 5):
    """Find apartment matches for a specific profile"""
    try:
        profile = matcher.get_profile_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Find apartment matches
        apartment_matches = matcher.find_apartment_matches_for_profile(profile, limit)
        
        return {
            "profile_id": profile_id,
            "profile_name": profile.name,
            "matches": apartment_matches,
            "count": len(apartment_matches)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.get("/best-apartment/{profile_id}", response_model=Dict[str, Any])
async def get_best_apartment(profile_id: str):
    """Return the single best apartment match for a given profile"""
    try:
        profile = matcher.get_profile_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        matches = matcher.find_apartment_matches_for_profile(profile, limit=1)
        if not matches:
            return {"profile_id": profile_id, "best_match": None}

        return {
            "profile_id": profile_id,
            "best_match": matches[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.post("/recommendations", response_model=Dict[str, Any])
async def generate_recommendations():
    """Generate comprehensive recommendations using Supabase data"""
    try:
        recommendations = matcher.generate_supabase_recommendations()
        
        return {
            "recommendations": recommendations,
            "generated_at": "now"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.get("/data-summary", response_model=DataSummaryResponse)
async def get_data_summary():
    """Get summary of available data from Supabase"""
    try:
        profiles = matcher.get_all_profiles()
        
        return DataSummaryResponse(
            apartments={
                "count": len(matcher.apartments),
                "names": [apt["name"] for apt in matcher.apartments]
            },
            profiles={
                "count": len(profiles),
                "names": [profile.name for profile in profiles],
                "years": list(set(profile.year for profile in profiles)),
                "majors": list(set(profile.major for profile in profiles if profile.major))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.get("/apartments", response_model=Dict[str, Any])
async def get_apartments():
    """Get all apartments from Supabase database"""
    try:
        return {
            "apartments": matcher.apartments,
            "count": len(matcher.apartments)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: str):
    """Delete a profile by ID"""
    try:
        # Use the supabase matcher to delete the profile
        success = matcher.delete_profile(profile_id)
        
        if success:
            return {"message": "Profile deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.post("/profiles/clear-temp")
async def clear_temp_profiles():
    """Clear temporary profiles after user session"""
    try:
        success = matcher.profiles_connector.clear_temp_profiles()
        
        if success:
            return {"message": "Temporary profiles cleared successfully"}
        else:
            return {"message": "No temporary profiles to clear"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
