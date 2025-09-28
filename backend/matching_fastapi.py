#!/usr/bin/env python3
"""
FastAPI endpoints for roommate matching system
Integrates with the main FastAPI app
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
import json
from roommate_matcher import RoommateMatcher, RoommatePreferences, PreferenceLevel

# Create router for matching endpoints
matching_router = APIRouter(prefix="/matching", tags=["matching"])

# Initialize the matcher
matcher = RoommateMatcher()

# In-memory storage for roommates (in production, use database)
roommates_storage = []

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
    gender_preference: Optional[str] = Field(default=None, description="Gender preference for roommate")
    age_range: Optional[List[int]] = Field(default=None, description="Preferred age range [min, max]")
    move_in_date: Optional[str] = Field(default=None, description="Preferred move-in date")
    lease_length: Optional[int] = Field(default=None, description="Preferred lease length in months")

class RoommateMatchRequest(BaseModel):
    min_compatibility: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum compatibility score")

class RoommateResponse(BaseModel):
    name: str
    email: str
    budget_min: int
    budget_max: int
    preferred_bedrooms: int
    cleanliness: str
    noise_level: str
    study_time: str
    social_level: str
    sleep_schedule: str
    pet_friendly: bool
    smoking: bool
    gender_preference: Optional[str]
    age_range: Optional[List[int]]
    move_in_date: Optional[str]
    lease_length: Optional[int]

class RoommateMatchResponse(BaseModel):
    roommate1: RoommateResponse
    roommate2: RoommateResponse
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

class DataSummaryResponse(BaseModel):
    apartments: Dict[str, Any]
    restaurants: Dict[str, Any]
    amenities: Dict[str, Any]
    roommates: Dict[str, Any]

def convert_preference_string_to_enum(preference_str: str) -> PreferenceLevel:
    """Convert string preference to PreferenceLevel enum"""
    preference_mapping = {
        'VERY_LOW': PreferenceLevel.VERY_LOW,
        'LOW': PreferenceLevel.LOW,
        'MEDIUM': PreferenceLevel.MEDIUM,
        'HIGH': PreferenceLevel.HIGH,
        'VERY_HIGH': PreferenceLevel.VERY_HIGH
    }
    return preference_mapping.get(preference_str.upper(), PreferenceLevel.MEDIUM)

@matching_router.post("/roommate-preferences", response_model=Dict[str, Any])
async def create_roommate_profile(request: RoommatePreferencesRequest):
    """Create a new roommate profile with preferences"""
    try:
        # Convert string preferences to enums
        roommate = RoommatePreferences(
            name=request.name,
            email=request.email,
            budget_min=request.budget_min,
            budget_max=request.budget_max,
            preferred_bedrooms=request.preferred_bedrooms,
            cleanliness=convert_preference_string_to_enum(request.cleanliness),
            noise_level=convert_preference_string_to_enum(request.noise_level),
            study_time=convert_preference_string_to_enum(request.study_time),
            social_level=convert_preference_string_to_enum(request.social_level),
            sleep_schedule=convert_preference_string_to_enum(request.sleep_schedule),
            pet_friendly=request.pet_friendly,
            smoking=request.smoking,
            gender_preference=request.gender_preference,
            age_range=tuple(request.age_range) if request.age_range else None,
            move_in_date=request.move_in_date,
            lease_length=request.lease_length
        )
        
        # Check if roommate already exists
        existing_roommate = next((r for r in roommates_storage if r.email == roommate.email), None)
        if existing_roommate:
            # Update existing roommate
            index = roommates_storage.index(existing_roommate)
            roommates_storage[index] = roommate
            message = "Roommate profile updated successfully"
        else:
            # Add new roommate
            roommates_storage.append(roommate)
            message = "Roommate profile created successfully"
        
        return {
            "message": message,
            "roommate": {
                "name": roommate.name,
                "email": roommate.email,
                "budget_min": roommate.budget_min,
                "budget_max": roommate.budget_max,
                "preferred_bedrooms": roommate.preferred_bedrooms
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.get("/roommate-preferences/{email}", response_model=RoommateResponse)
async def get_roommate_profile(email: str):
    """Get a roommate profile by email"""
    try:
        roommate = next((r for r in roommates_storage if r.email == email), None)
        if not roommate:
            raise HTTPException(status_code=404, detail="Roommate not found")
        
        return RoommateResponse(
            name=roommate.name,
            email=roommate.email,
            budget_min=roommate.budget_min,
            budget_max=roommate.budget_max,
            preferred_bedrooms=roommate.preferred_bedrooms,
            cleanliness=roommate.cleanliness.name,
            noise_level=roommate.noise_level.name,
            study_time=roommate.study_time.name,
            social_level=roommate.social_level.name,
            sleep_schedule=roommate.sleep_schedule.name,
            pet_friendly=roommate.pet_friendly,
            smoking=roommate.smoking,
            gender_preference=roommate.gender_preference,
            age_range=list(roommate.age_range) if roommate.age_range else None,
            move_in_date=roommate.move_in_date,
            lease_length=roommate.lease_length
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.get("/roommate-preferences", response_model=Dict[str, Any])
async def get_all_roommate_profiles():
    """Get all roommate profiles"""
    try:
        roommates_list = []
        for roommate in roommates_storage:
            roommate_dict = {
                "name": roommate.name,
                "email": roommate.email,
                "budget_min": roommate.budget_min,
                "budget_max": roommate.budget_max,
                "preferred_bedrooms": roommate.preferred_bedrooms,
                "cleanliness": roommate.cleanliness.name,
                "noise_level": roommate.noise_level.name,
                "study_time": roommate.study_time.name,
                "social_level": roommate.social_level.name,
                "sleep_schedule": roommate.sleep_schedule.name,
                "pet_friendly": roommate.pet_friendly,
                "smoking": roommate.smoking,
                "gender_preference": roommate.gender_preference,
                "age_range": list(roommate.age_range) if roommate.age_range else None,
                "move_in_date": roommate.move_in_date,
                "lease_length": roommate.lease_length
            }
            roommates_list.append(roommate_dict)
        
        return {
            "roommates": roommates_list,
            "count": len(roommates_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.post("/roommate-matches", response_model=Dict[str, Any])
async def find_roommate_matches(request: RoommateMatchRequest):
    """Find compatible roommate matches"""
    try:
        if len(roommates_storage) < 2:
            return {
                "message": "Need at least 2 roommates to find matches",
                "matches": []
            }
        
        # Find matches
        matches = matcher.find_roommate_matches(roommates_storage, request.min_compatibility)
        
        # Format response
        matches_list = []
        for roommate1, roommate2, compatibility in matches:
            matches_list.append({
                "roommate1": {
                    "name": roommate1.name,
                    "email": roommate1.email,
                    "cleanliness": roommate1.cleanliness.name,
                    "noise_level": roommate1.noise_level.name,
                    "study_time": roommate1.study_time.name,
                    "social_level": roommate1.social_level.name,
                    "sleep_schedule": roommate1.sleep_schedule.name,
                    "pet_friendly": roommate1.pet_friendly,
                    "smoking": roommate1.smoking
                },
                "roommate2": {
                    "name": roommate2.name,
                    "email": roommate2.email,
                    "cleanliness": roommate2.cleanliness.name,
                    "noise_level": roommate2.noise_level.name,
                    "study_time": roommate2.study_time.name,
                    "social_level": roommate2.social_level.name,
                    "sleep_schedule": roommate2.sleep_schedule.name,
                    "pet_friendly": roommate2.pet_friendly,
                    "smoking": roommate2.smoking
                },
                "compatibility_score": round(compatibility, 3),
                "compatibility_percentage": round(compatibility * 100, 1)
            })
        
        return {
            "matches": matches_list,
            "count": len(matches_list),
            "min_compatibility": request.min_compatibility
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.get("/apartment-matches/{email}", response_model=Dict[str, Any])
async def find_apartment_matches(email: str, limit: int = 5):
    """Find apartment matches for a specific roommate"""
    try:
        roommate = next((r for r in roommates_storage if r.email == email), None)
        if not roommate:
            raise HTTPException(status_code=404, detail="Roommate not found")
        
        # Find apartment matches
        apartment_matches = matcher.find_apartment_matches(roommate, limit)
        
        # Format response
        matches_list = []
        for match in apartment_matches:
            matches_list.append({
                "apartment_name": match.apartment_name,
                "apartment_address": match.apartment_address,
                "bedroom_count": match.bedroom_count,
                "price": match.price,
                "distance_to_vt": match.distance_to_vt,
                "amenities": match.amenities,
                "match_score": match.match_score,
                "match_percentage": round(match.match_score * 100, 1),
                "reasons": match.reasons,
                "roommate_compatibility": match.roommate_compatibility,
                "apartment_features": match.apartment_features
            })
        
        return {
            "roommate_email": email,
            "matches": matches_list,
            "count": len(matches_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.post("/recommendations", response_model=Dict[str, Any])
async def generate_recommendations():
    """Generate comprehensive recommendations for all roommates"""
    try:
        if len(roommates_storage) == 0:
            return {
                "message": "No roommates found. Please create roommate profiles first.",
                "recommendations": {
                    "roommate_matches": [],
                    "apartment_matches": {},
                    "summary": {
                        "total_roommates": 0,
                        "total_apartments": len(matcher.apartments),
                        "total_restaurants": len(matcher.restaurants),
                        "total_amenities": len(matcher.amenities)
                    }
                }
            }
        
        # Generate recommendations
        recommendations = matcher.generate_recommendations(roommates_storage)
        
        return {
            "recommendations": recommendations,
            "generated_at": "now"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@matching_router.get("/data-summary", response_model=DataSummaryResponse)
async def get_data_summary():
    """Get summary of available data"""
    try:
        return DataSummaryResponse(
            apartments={
                "count": len(matcher.apartments),
                "names": [apt["name"] for apt in matcher.apartments]
            },
            restaurants={
                "count": len(matcher.restaurants),
                "names": [rest["name"] for rest in matcher.restaurants]
            },
            amenities={
                "count": len(matcher.amenities),
                "categories": list(set(amenity["category"] for amenity in matcher.amenities))
            },
            roommates={
                "count": len(roommates_storage),
                "emails": [r.email for r in roommates_storage]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
