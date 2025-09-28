#!/usr/bin/env python3
"""
Supabase-integrated Roommate Matching System
Uses existing Profile and ApartmentComplex models from Supabase
"""

import json
import math
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from sqlmodel import Session, create_engine, select
from models import Profile, ApartmentComplex, ProfileCreate, ProfileRead
from roommate_matcher import PreferenceLevel, RoommatePreferences, ApartmentMatch
from supabase_profiles_connector import SupabaseProfilesConnector
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseRoommateMatcher:
    def __init__(self):
        # Use Supabase PostgreSQL if available, otherwise fallback to SQLite
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
        
        self.engine = create_engine(DATABASE_URL)
        
        # Load apartments from database
        self.apartments = self.load_apartments_from_db()
        print(f"✅ Loaded {len(self.apartments)} apartments from Supabase database")
        
        # Initialize Supabase profiles connector
        self.profiles_connector = SupabaseProfilesConnector()

        # Load external datasets (restaurants and amenities) for lifestyle scoring
        base_dir = os.path.dirname(__file__)
        restaurants_path = os.path.join(base_dir, "restaurants_data.json")
        amenities_path = os.path.join(base_dir, "amenities_data.json")
        try:
            with open(restaurants_path, "r") as f:
                self.restaurants: List[Dict[str, Any]] = json.load(f)
        except Exception:
            self.restaurants = []
        try:
            with open(amenities_path, "r") as f:
                self.external_amenities: List[Dict[str, Any]] = json.load(f)
        except Exception:
            self.external_amenities = []

    def load_apartments_from_db(self) -> List[Dict[str, Any]]:
        """Load apartments from the Supabase database"""
        apartments = []
        with Session(self.engine) as session:
            db_apartments = session.exec(select(ApartmentComplex)).all()
            
            for apt in db_apartments:
                apartment_dict = {
                    'name': apt.name,
                    'address': apt.address or '',
                    'studio_price': apt.studio_cost,
                    'one_bedroom_price': apt.one_bedroom_cost,
                    'two_bedroom_price': apt.two_bedroom_cost,
                    'three_bedroom_price': apt.three_bedroom_cost,
                    'four_bedroom_price': apt.four_bedroom_cost,
                    'five_bedroom_price': apt.five_bedroom_cost,
                    'distance_to_vt': apt.distance_to_burruss or 0.0,
                    'amenities': self.parse_amenities(apt),
                    'pet_friendly': apt.pets_allowed or False,
                    'parking': 'Free' if apt.parking_included else 'Not included',
                    'gym': 'Fitness Center' in self.parse_amenities(apt),
                    'pool': 'Pool' in self.parse_amenities(apt),
                    'laundry': apt.laundry or 'Not specified',
                    'wifi_included': 'Internet' in (apt.utilities_included or ''),
                    'utilities_included': self.parse_utilities(apt.utilities_included),
                    'bus_stop_nearby': apt.bus_stop_nearby or False,
                    'phone': apt.phone_number,
                    'website': None,
                    'description': apt.notes
                }
                apartments.append(apartment_dict)
        
        return apartments

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile by ID from Supabase"""
        try:
            with Session(self.engine) as session:
                profile = session.get(Profile, profile_id)
                if profile:
                    session.delete(profile)
                    session.commit()
                    return True
                return False
        except Exception as e:
            print(f"Error deleting profile {profile_id}: {e}")
            return False

    def parse_amenities(self, apartment: ApartmentComplex) -> List[str]:
        """Parse amenities from apartment data"""
        amenities = []
        
        if apartment.pets_allowed:
            amenities.append('Pet Friendly')
        if apartment.parking_included:
            amenities.append('Parking')
        if apartment.laundry:
            amenities.append('Laundry')
        if apartment.furniture_included:
            amenities.append('Furnished')
        
        # Add common amenities based on apartment name patterns
        name_lower = apartment.name.lower()
        if 'pool' in name_lower or 'aqua' in name_lower:
            amenities.append('Pool')
        if 'fitness' in name_lower or 'gym' in name_lower or 'health' in name_lower:
            amenities.append('Fitness Center')
        
        return amenities

    def parse_utilities(self, utilities_str: Optional[str]) -> List[str]:
        """Parse utilities from JSON string"""
        if not utilities_str:
            return []
        
        try:
            if utilities_str.startswith('[') or utilities_str.startswith('{'):
                return json.loads(utilities_str)
            else:
                # Handle comma-separated utilities
                return [util.strip() for util in utilities_str.split(',') if util.strip()]
        except:
            return []

    def convert_profile_to_roommate_preferences(self, profile: Profile) -> RoommatePreferences:
        """Convert Supabase Profile to RoommatePreferences"""
        # Convert integer preferences to PreferenceLevel enum
        def int_to_preference_level(value: int) -> PreferenceLevel:
            if value <= 1:
                return PreferenceLevel.VERY_LOW
            elif value == 2:
                return PreferenceLevel.LOW
            elif value == 3:
                return PreferenceLevel.MEDIUM
            elif value == 4:
                return PreferenceLevel.HIGH
            else:
                return PreferenceLevel.VERY_HIGH
        
        # Extract email from profile name or use a generated one
        email = f"{profile.name.lower().replace(' ', '.')}@vt.edu"
        
        return RoommatePreferences(
            name=profile.name,
            email=email,
            budget_min=profile.budget,
            budget_max=profile.budget + 200,  # Add buffer
            preferred_bedrooms=2,  # Default, could be made configurable
            cleanliness=int_to_preference_level(profile.cleanliness),
            noise_level=int_to_preference_level(profile.noise),
            study_time=int_to_preference_level(profile.study_time),
            social_level=int_to_preference_level(profile.social),
            sleep_schedule=int_to_preference_level(profile.sleep),
            pet_friendly='pets' in (profile.tags or []),
            smoking='smoking' in (profile.tags or [])
        )

    def get_all_profiles(self) -> List[Profile]:
        """Get all profiles from Supabase database"""
        with Session(self.engine) as session:
            return session.exec(select(Profile)).all()

    def create_profile_from_roommate_preferences(self, preferences: RoommatePreferences) -> Profile:
        """Create a Profile in Supabase from RoommatePreferences"""
        
        # Convert PreferenceLevel back to integer
        def preference_level_to_int(level: PreferenceLevel) -> int:
            return level.value
        
        # Generate tags based on preferences
        tags = []
        if preferences.pet_friendly:
            tags.append('pets')
        if preferences.smoking:
            tags.append('smoking')
        
        profile_data = ProfileCreate(
            name=preferences.name,
            year='Junior',  # Default, could be made configurable
            major='Computer Science',  # Default, could be made configurable
            budget=preferences.budget_min,
            move_in=None,
            tags=tags,
            cleanliness=preference_level_to_int(preferences.cleanliness),
            noise=preference_level_to_int(preferences.noise_level),
            study_time=preference_level_to_int(preferences.study_time),
            social=preference_level_to_int(preferences.social_level),
            sleep=preference_level_to_int(preferences.sleep_schedule)
        )
        
        with Session(self.engine) as session:
            profile = Profile.model_validate(profile_data)
            session.add(profile)
            session.commit()
            session.refresh(profile)
            return profile

    def calculate_compatibility_score(self, profile1: Profile, profile2: Profile) -> float:
        """Calculate compatibility score between two Supabase profiles"""
        score = 0.0
        max_score = 0.0
        
        # Budget compatibility (20% weight)
        budget_diff = abs(profile1.budget - profile2.budget) / max(profile1.budget, profile2.budget)
        budget_compat = max(0, 1 - budget_diff)
        score += budget_compat * 0.2
        max_score += 0.2
        
        # Cleanliness compatibility (25% weight)
        cleanliness_diff = abs(profile1.cleanliness - profile2.cleanliness) / 5.0
        cleanliness_compat = max(0, 1 - cleanliness_diff)
        score += cleanliness_compat * 0.25
        max_score += 0.25
        
        # Noise level compatibility (20% weight)
        noise_diff = abs(profile1.noise - profile2.noise) / 5.0
        noise_compat = max(0, 1 - noise_diff)
        score += noise_compat * 0.2
        max_score += 0.2
        
        # Study time compatibility (15% weight)
        study_diff = abs(profile1.study_time - profile2.study_time) / 5.0
        study_compat = max(0, 1 - study_diff)
        score += study_compat * 0.15
        max_score += 0.15
        
        # Social level compatibility (10% weight)
        social_diff = abs(profile1.social - profile2.social) / 5.0
        social_compat = max(0, 1 - social_diff)
        score += social_compat * 0.1
        max_score += 0.1
        
        # Sleep schedule compatibility (10% weight)
        sleep_diff = abs(profile1.sleep - profile2.sleep) / 5.0
        sleep_compat = max(0, 1 - sleep_diff)
        score += sleep_compat * 0.1
        max_score += 0.1
        
        # Tag compatibility (bonus/penalty)
        tags1 = set(profile1.tags or [])
        tags2 = set(profile2.tags or [])
        
        # Pet compatibility
        if ('pets' in tags1) == ('pets' in tags2):
            score += 0.05
            max_score += 0.05
        else:
            score -= 0.05
            max_score += 0.05
        
        # Smoking compatibility
        if ('smoking' in tags1) == ('smoking' in tags2):
            score += 0.05
            max_score += 0.05
        else:
            score -= 0.1
            max_score += 0.1
        
        return max(0, min(1, score / max_score)) if max_score > 0 else 0

    def find_roommate_matches_from_db(self, min_compatibility: float = 0.05) -> List[Tuple[Profile, Profile, float]]:
        """Find compatible roommate matches from Supabase database"""
        profiles = self.get_all_profiles()
        matches = []
        
        for i in range(len(profiles)):
            for j in range(i + 1, len(profiles)):
                compatibility = self.calculate_compatibility_score(profiles[i], profiles[j])
                if compatibility >= min_compatibility:
                    matches.append((profiles[i], profiles[j], compatibility))
        
        # Sort by compatibility score
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches

    def calculate_apartment_score_for_profile(self, profile: Profile, apartment: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate how well an apartment matches a Supabase profile"""
        score = 0.0
        max_score = 0.0
        reasons = []
        
        # Budget compatibility (30% weight)
        if apartment.get('two_bedroom_price'):
            apartment_price = self.extract_apartment_price(apartment, 2)
            if apartment_price:
                if profile.budget <= apartment_price <= profile.budget + 200:
                    score += 1.0 * 0.3
                    reasons.append(f"Price ${apartment_price} fits your budget (${profile.budget})")
                elif apartment_price < profile.budget:
                    score += 0.8 * 0.3
                    reasons.append(f"Price ${apartment_price} is below your budget")
                else:
                    score += max(0, (profile.budget / apartment_price)) * 0.3
                    reasons.append(f"Price ${apartment_price} is above your budget")
        max_score += 0.3
        
        # Distance to VT (20% weight)
        if apartment.get('distance_to_vt'):
            distance = apartment['distance_to_vt']
            if distance <= 1.0:
                score += 1.0 * 0.2
                reasons.append(f"Very close to VT: {distance} miles")
            elif distance <= 2.0:
                score += 0.8 * 0.2
                reasons.append(f"Close to VT: {distance} miles")
            elif distance <= 3.0:
                score += 0.6 * 0.2
                reasons.append(f"Moderate distance to VT: {distance} miles")
            else:
                score += 0.4 * 0.2
                reasons.append(f"Far from VT: {distance} miles")
        max_score += 0.2
        
        # Amenities compatibility (25% weight)
        amenities_score = 0
        apartment_amenities = apartment.get('amenities', [])
        
        # Check for preferred amenities based on profile preferences
        if profile.cleanliness >= 4 and 'Laundry' in apartment_amenities:
            amenities_score += 0.3
            reasons.append("Has laundry facilities (good for cleanliness)")
        
        if profile.social >= 4 and 'Pool' in apartment_amenities:
            amenities_score += 0.2
            reasons.append("Has pool (good for socializing)")
        
        if profile.noise <= 2 and 'Fitness Center' in apartment_amenities:
            amenities_score += 0.2
            reasons.append("Has fitness center (quiet activity)")
        
        if profile.tags and 'pets' in profile.tags and apartment.get('pet_friendly'):
            amenities_score += 0.3
            reasons.append("Pet-friendly apartment")
        
        score += amenities_score * 0.25
        max_score += 0.25
        
        # Study environment (15% weight)
        study_score = 0
        if profile.study_time >= 4:
            if 'WiFi' in apartment_amenities or apartment.get('wifi_included'):
                study_score += 0.5
                reasons.append("Includes WiFi (good for studying)")
            if not apartment.get('pool'):  # Pool can be noisy
                study_score += 0.5
                reasons.append("Quiet environment for studying")
        
        score += study_score * 0.15
        max_score += 0.15
        
        # Parking (10% weight)
        if apartment.get('parking'):
            score += 0.8 * 0.1
            reasons.append(f"Parking available: {apartment['parking']}")
        max_score += 0.1

        # Lifestyle proximity using restaurants and city amenities (10% weight)
        # Heuristic: apartments closer to VT tend to be closer to restaurants/amenities in provided datasets
        lifestyle_weight = 0.10
        lifestyle_score = 0.0
        vt_distance = apartment.get('distance_to_vt', apartment.get('distance_to_burruss', None))
        if vt_distance is not None:
            # Prefer <= 2 miles strongly, linearly decay until 5 miles
            if vt_distance <= 2.0:
                lifestyle_score = 1.0
            elif vt_distance >= 5.0:
                lifestyle_score = 0.2
            else:
                lifestyle_score = max(0.2, 1.0 - (vt_distance - 2.0) / 3.0)

            # Tailor to profile preferences: social/study bias towards being near campus hotspots
            highlight_names: List[str] = []
            if profile.social >= 4 and self.restaurants:
                # Mention up to 2 popular nearby restaurants
                highlight_names.extend([r.get('name') for r in self.restaurants[:2]])
            if profile.study_time >= 4:
                # Mention library if present in dataset
                lib = next((a for a in self.external_amenities if (a.get('category') == 'library')), None)
                if lib:
                    highlight_names.append(lib.get('name'))

            if highlight_names:
                reasons.append(f"Close to campus hotspots: {', '.join(n for n in highlight_names if n)}")

        score += lifestyle_score * lifestyle_weight
        max_score += lifestyle_weight

        # Shopping proximity (5% weight) - simple preference for being within ~2.5 miles of VT
        shopping_weight = 0.05
        shopping_score = 0.0
        if vt_distance is not None:
            if vt_distance <= 2.5:
                shopping_score = 1.0
                # Mention a shopping amenity if available
                shop = next((a for a in self.external_amenities if a.get('category') == 'shopping'), None)
                if shop:
                    reasons.append(f"Convenient shopping nearby (e.g., {shop.get('name')})")
            elif vt_distance <= 4.0:
                shopping_score = 0.6
            else:
                shopping_score = 0.3

        score += shopping_score * shopping_weight
        max_score += shopping_weight
        
        return score / max_score if max_score > 0 else 0, reasons

    def extract_apartment_price(self, apartment: Dict[str, Any], bedroom_count: int) -> Optional[int]:
        """Extract price for specific bedroom count"""
        price_field = {
            0: 'studio_price',
            1: 'one_bedroom_price',
            2: 'two_bedroom_price',
            3: 'three_bedroom_price',
            4: 'four_bedroom_price',
            5: 'five_bedroom_price'
        }.get(bedroom_count)
        
        if price_field and apartment.get(price_field):
            price_str = apartment[price_field]
            # Extract number from price string like "$1200" or "$1200-$1500"
            import re
            numbers = re.findall(r'\d+', price_str)
            if numbers:
                return int(numbers[0])  # Use first number (minimum price)
        return None

    def find_apartment_matches_for_profile(self, profile: Profile, limit: int = 5) -> List[Dict[str, Any]]:
        """Find best apartment matches for a Supabase profile"""
        apartment_matches = []
        
        for apartment in self.apartments:
            score, reasons = self.calculate_apartment_score_for_profile(profile, apartment)
            
            match = {
                'apartment_name': apartment['name'],
                'apartment_address': apartment['address'],
                'bedroom_count': 2,  # Default for now
                'price': f"${self.extract_apartment_price(apartment, 2) or 'N/A'}",
                'distance_to_vt': apartment.get('distance_to_vt', 0),
                'amenities': apartment.get('amenities', []),
                'match_score': score,
                'match_percentage': round(score * 100, 1),
                'reasons': reasons,
                'roommate_compatibility': 0.5,  # Default neutral score
                'apartment_features': apartment
            }
            
            apartment_matches.append(match)
        
        # Sort by match score
        apartment_matches.sort(key=lambda x: x['match_score'], reverse=True)
        return apartment_matches[:limit]

    def get_profile_by_id(self, profile_id: str) -> Optional[Profile]:
        """Get a profile by ID from Supabase"""
        from uuid import UUID
        try:
            with Session(self.engine) as session:
                return session.get(Profile, UUID(profile_id))
        except:
            return None

    def generate_supabase_recommendations(self) -> Dict[str, Any]:
        """Generate comprehensive recommendations using Supabase data"""
        profiles = self.get_all_profiles()
        
        recommendations = {
            'roommate_matches': [],
            'apartment_matches': {},
            'summary': {
                'total_roommates': len(profiles),
                'total_apartments': len(self.apartments),
                'total_restaurants': 8,  # From our static data
                'total_amenities': 8   # From our static data
            }
        }
        
        # Find roommate matches
        roommate_matches = self.find_roommate_matches_from_db()
        for profile1, profile2, compatibility in roommate_matches:
            recommendations['roommate_matches'].append({
                'roommate1': {
                    'id': str(profile1.id),
                    'name': profile1.name,
                    'year': profile1.year,
                    'major': profile1.major,
                    'budget': profile1.budget,
                    'cleanliness': profile1.cleanliness,
                    'noise_level': profile1.noise,
                    'study_time': profile1.study_time,
                    'social_level': profile1.social,
                    'sleep_schedule': profile1.sleep,
                    'tags': profile1.tags
                },
                'roommate2': {
                    'id': str(profile2.id),
                    'name': profile2.name,
                    'year': profile2.year,
                    'major': profile2.major,
                    'budget': profile2.budget,
                    'cleanliness': profile2.cleanliness,
                    'noise_level': profile2.noise,
                    'study_time': profile2.study_time,
                    'social_level': profile2.social,
                    'sleep_schedule': profile2.sleep,
                    'tags': profile2.tags
                },
                'compatibility_score': round(compatibility, 3),
                'compatibility_percentage': round(compatibility * 100, 1)
            })
        
        # Find apartment matches for each profile
        for profile in profiles:
            apartment_matches = self.find_apartment_matches_for_profile(profile)
            recommendations['apartment_matches'][str(profile.id)] = apartment_matches
        
        return recommendations
