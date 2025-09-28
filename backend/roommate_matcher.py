#!/usr/bin/env python3
"""
Roommate Matching System
Matches roommates to apartments based on preferences and compatibility
"""

import json
import math
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class PreferenceLevel(Enum):
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5

@dataclass
class RoommatePreferences:
    name: str
    email: str
    budget_min: int
    budget_max: int
    preferred_bedrooms: int
    cleanliness: PreferenceLevel
    noise_level: PreferenceLevel
    study_time: PreferenceLevel
    social_level: PreferenceLevel
    sleep_schedule: PreferenceLevel  # Early bird vs night owl
    pet_friendly: bool
    smoking: bool
    gender_preference: Optional[str] = None
    age_range: Optional[Tuple[int, int]] = None
    move_in_date: Optional[str] = None
    lease_length: Optional[int] = None

@dataclass
class ApartmentMatch:
    apartment_name: str
    apartment_address: str
    bedroom_count: int
    price: str
    distance_to_vt: float
    amenities: List[str]
    match_score: float
    reasons: List[str]
    roommate_compatibility: float
    apartment_features: Dict[str, Any]

class RoommateMatcher:
    def __init__(self):
        self.apartments = []
        self.restaurants = []
        self.amenities = []
        self.load_data()

    def load_data(self):
        """Load apartment, restaurant, and amenity data"""
        try:
            with open('apartments_data.json', 'r') as f:
                self.apartments = json.load(f)
            
            with open('restaurants_data.json', 'r') as f:
                self.restaurants = json.load(f)
            
            with open('amenities_data.json', 'r') as f:
                self.amenities = json.load(f)
            
            print(f"✅ Loaded {len(self.apartments)} apartments, {len(self.restaurants)} restaurants, {len(self.amenities)} amenities")
        except FileNotFoundError as e:
            print(f"❌ Error loading data: {e}")
            print("Please run comprehensive_data_scraper.py first")

    def calculate_compatibility_score(self, roommate1: RoommatePreferences, roommate2: RoommatePreferences) -> float:
        """Calculate compatibility score between two roommates"""
        score = 0.0
        max_score = 0.0
        
        # Budget compatibility (20% weight)
        budget_diff = abs(roommate1.budget_max - roommate2.budget_max) / max(roommate1.budget_max, roommate2.budget_max)
        budget_compat = max(0, 1 - budget_diff)
        score += budget_compat * 0.2
        max_score += 0.2
        
        # Cleanliness compatibility (25% weight)
        cleanliness_diff = abs(roommate1.cleanliness.value - roommate2.cleanliness.value)
        cleanliness_compat = max(0, 1 - (cleanliness_diff / 4))
        score += cleanliness_compat * 0.25
        max_score += 0.25
        
        # Noise level compatibility (20% weight)
        noise_diff = abs(roommate1.noise_level.value - roommate2.noise_level.value)
        noise_compat = max(0, 1 - (noise_diff / 4))
        score += noise_compat * 0.2
        max_score += 0.2
        
        # Study time compatibility (15% weight)
        study_diff = abs(roommate1.study_time.value - roommate2.study_time.value)
        study_compat = max(0, 1 - (study_diff / 4))
        score += study_compat * 0.15
        max_score += 0.15
        
        # Social level compatibility (10% weight)
        social_diff = abs(roommate1.social_level.value - roommate2.social_level.value)
        social_compat = max(0, 1 - (social_diff / 4))
        score += social_compat * 0.1
        max_score += 0.1
        
        # Sleep schedule compatibility (10% weight)
        sleep_diff = abs(roommate1.sleep_schedule.value - roommate2.sleep_schedule.value)
        sleep_compat = max(0, 1 - (sleep_diff / 4))
        score += sleep_compat * 0.1
        max_score += 0.1
        
        # Pet compatibility bonus/penalty
        if roommate1.pet_friendly == roommate2.pet_friendly:
            score += 0.05
            max_score += 0.05
        else:
            score -= 0.05
            max_score += 0.05
        
        # Smoking compatibility
        if roommate1.smoking == roommate2.smoking:
            score += 0.05
            max_score += 0.05
        else:
            score -= 0.1
            max_score += 0.1
        
        return max(0, min(1, score / max_score)) if max_score > 0 else 0

    def calculate_apartment_score(self, roommate: RoommatePreferences, apartment: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate how well an apartment matches a roommate's preferences"""
        score = 0.0
        max_score = 0.0
        reasons = []
        
        # Budget compatibility (30% weight)
        apartment_price = self.extract_apartment_price(apartment, roommate.preferred_bedrooms)
        if apartment_price:
            if roommate.budget_min <= apartment_price <= roommate.budget_max:
                score += 1.0 * 0.3
                reasons.append(f"Price ${apartment_price} fits your budget (${roommate.budget_min}-${roommate.budget_max})")
            elif apartment_price < roommate.budget_min:
                score += 0.8 * 0.3
                reasons.append(f"Price ${apartment_price} is below your minimum budget")
            else:
                score += max(0, (roommate.budget_max / apartment_price)) * 0.3
                reasons.append(f"Price ${apartment_price} is above your budget")
        max_score += 0.3
        
        # Bedroom count compatibility (20% weight)
        if self.get_bedroom_count(apartment) == roommate.preferred_bedrooms:
            score += 1.0 * 0.2
            reasons.append(f"Perfect bedroom count: {roommate.preferred_bedrooms}")
        else:
            score += 0.5 * 0.2
            reasons.append(f"Bedroom count: {self.get_bedroom_count(apartment)} (preferred: {roommate.preferred_bedrooms})")
        max_score += 0.2
        
        # Distance to VT (15% weight)
        if apartment.get('distance_to_vt'):
            distance = apartment['distance_to_vt']
            if distance <= 1.0:
                score += 1.0 * 0.15
                reasons.append(f"Very close to VT: {distance} miles")
            elif distance <= 2.0:
                score += 0.8 * 0.15
                reasons.append(f"Close to VT: {distance} miles")
            elif distance <= 3.0:
                score += 0.6 * 0.15
                reasons.append(f"Moderate distance to VT: {distance} miles")
            else:
                score += 0.4 * 0.15
                reasons.append(f"Far from VT: {distance} miles")
        max_score += 0.15
        
        # Amenities compatibility (15% weight)
        amenities_score = 0
        apartment_amenities = apartment.get('amenities', [])
        
        # Check for preferred amenities based on preferences
        if roommate.cleanliness.value >= 4 and 'Laundry' in apartment_amenities:
            amenities_score += 0.3
            reasons.append("Has laundry facilities (good for cleanliness)")
        
        if roommate.social_level.value >= 4 and 'Pool' in apartment_amenities:
            amenities_score += 0.2
            reasons.append("Has pool (good for socializing)")
        
        if roommate.noise_level.value <= 2 and 'Fitness Center' in apartment_amenities:
            amenities_score += 0.2
            reasons.append("Has fitness center (quiet activity)")
        
        if roommate.pet_friendly and apartment.get('pet_friendly'):
            amenities_score += 0.3
            reasons.append("Pet-friendly apartment")
        
        score += amenities_score * 0.15
        max_score += 0.15
        
        # Study environment (10% weight)
        study_score = 0
        if roommate.study_time.value >= 4:
            if 'WiFi' in apartment_amenities or apartment.get('wifi_included'):
                study_score += 0.5
                reasons.append("Includes WiFi (good for studying)")
            if not apartment.get('pool'):  # Pool can be noisy
                study_score += 0.5
                reasons.append("Quiet environment for studying")
        
        score += study_score * 0.1
        max_score += 0.1
        
        # Parking (10% weight)
        if apartment.get('parking'):
            score += 0.8 * 0.1
            reasons.append(f"Parking available: {apartment['parking']}")
        max_score += 0.1
        
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

    def get_bedroom_count(self, apartment: Dict[str, Any]) -> int:
        """Get the maximum bedroom count available"""
        bedroom_counts = []
        for i in range(6):
            price_field = {
                0: 'studio_price',
                1: 'one_bedroom_price',
                2: 'two_bedroom_price',
                3: 'three_bedroom_price',
                4: 'four_bedroom_price',
                5: 'five_bedroom_price'
            }.get(i)
            
            if apartment.get(price_field):
                bedroom_counts.append(i)
        
        return max(bedroom_counts) if bedroom_counts else 1

    def find_roommate_matches(self, roommates: List[RoommatePreferences], min_compatibility: float = 0.6) -> List[Tuple[RoommatePreferences, RoommatePreferences, float]]:
        """Find compatible roommate pairs"""
        matches = []
        
        for i in range(len(roommates)):
            for j in range(i + 1, len(roommates)):
                compatibility = self.calculate_compatibility_score(roommates[i], roommates[j])
                if compatibility >= min_compatibility:
                    matches.append((roommates[i], roommates[j], compatibility))
        
        # Sort by compatibility score
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches

    def find_apartment_matches(self, roommate: RoommatePreferences, limit: int = 5) -> List[ApartmentMatch]:
        """Find best apartment matches for a roommate"""
        apartment_matches = []
        
        for apartment in self.apartments:
            score, reasons = self.calculate_apartment_score(roommate, apartment)
            
            # Calculate roommate compatibility (placeholder - would need other roommates)
            roommate_compatibility = 0.5  # Default neutral score
            
            match = ApartmentMatch(
                apartment_name=apartment['name'],
                apartment_address=apartment['address'],
                bedroom_count=self.get_bedroom_count(apartment),
                price=f"${self.extract_apartment_price(apartment, roommate.preferred_bedrooms) or 'N/A'}",
                distance_to_vt=apartment.get('distance_to_vt', 0),
                amenities=apartment.get('amenities', []),
                match_score=score,
                reasons=reasons,
                roommate_compatibility=roommate_compatibility,
                apartment_features=apartment
            )
            
            apartment_matches.append(match)
        
        # Sort by match score
        apartment_matches.sort(key=lambda x: x.match_score, reverse=True)
        return apartment_matches[:limit]

    def generate_recommendations(self, roommates: List[RoommatePreferences]) -> Dict[str, Any]:
        """Generate comprehensive recommendations for all roommates"""
        recommendations = {
            'roommate_matches': [],
            'apartment_matches': {},
            'summary': {
                'total_roommates': len(roommates),
                'total_apartments': len(self.apartments),
                'total_restaurants': len(self.restaurants),
                'total_amenities': len(self.amenities)
            }
        }
        
        # Find roommate matches
        roommate_matches = self.find_roommate_matches(roommates)
        for roommate1, roommate2, compatibility in roommate_matches:
            # Convert PreferenceLevel enums to strings for JSON serialization
            roommate1_dict = asdict(roommate1)
            roommate2_dict = asdict(roommate2)
            
            # Convert enums to strings
            for key, value in roommate1_dict.items():
                if isinstance(value, PreferenceLevel):
                    roommate1_dict[key] = value.name
                elif isinstance(value, tuple):
                    roommate1_dict[key] = list(value)
            
            for key, value in roommate2_dict.items():
                if isinstance(value, PreferenceLevel):
                    roommate2_dict[key] = value.name
                elif isinstance(value, tuple):
                    roommate2_dict[key] = list(value)
            
            recommendations['roommate_matches'].append({
                'roommate1': roommate1_dict,
                'roommate2': roommate2_dict,
                'compatibility_score': compatibility,
                'compatibility_percentage': round(compatibility * 100, 1)
            })
        
        # Find apartment matches for each roommate
        for roommate in roommates:
            apartment_matches = self.find_apartment_matches(roommate)
            recommendations['apartment_matches'][roommate.email] = [
                {
                    'apartment_name': match.apartment_name,
                    'apartment_address': match.apartment_address,
                    'bedroom_count': match.bedroom_count,
                    'price': match.price,
                    'distance_to_vt': match.distance_to_vt,
                    'amenities': match.amenities,
                    'match_score': round(match.match_score, 3),
                    'match_percentage': round(match.match_score * 100, 1),
                    'reasons': match.reasons,
                    'roommate_compatibility': round(match.roommate_compatibility, 3)
                }
                for match in apartment_matches
            ]
        
        return recommendations

def main():
    """Example usage of the roommate matching system"""
    matcher = RoommateMatcher()
    
    # Example roommates
    roommates = [
        RoommatePreferences(
            name="Alice Johnson",
            email="alice@vt.edu",
            budget_min=800,
            budget_max=1200,
            preferred_bedrooms=2,
            cleanliness=PreferenceLevel.HIGH,
            noise_level=PreferenceLevel.LOW,
            study_time=PreferenceLevel.VERY_HIGH,
            social_level=PreferenceLevel.MEDIUM,
            sleep_schedule=PreferenceLevel.HIGH,  # Early bird
            pet_friendly=True,
            smoking=False
        ),
        RoommatePreferences(
            name="Bob Smith",
            email="bob@vt.edu",
            budget_min=900,
            budget_max=1300,
            preferred_bedrooms=2,
            cleanliness=PreferenceLevel.MEDIUM,
            noise_level=PreferenceLevel.MEDIUM,
            study_time=PreferenceLevel.MEDIUM,
            social_level=PreferenceLevel.HIGH,
            sleep_schedule=PreferenceLevel.LOW,  # Night owl
            pet_friendly=False,
            smoking=False
        ),
        RoommatePreferences(
            name="Carol Davis",
            email="carol@vt.edu",
            budget_min=700,
            budget_max=1100,
            preferred_bedrooms=3,
            cleanliness=PreferenceLevel.VERY_HIGH,
            noise_level=PreferenceLevel.VERY_LOW,
            study_time=PreferenceLevel.HIGH,
            social_level=PreferenceLevel.LOW,
            sleep_schedule=PreferenceLevel.HIGH,
            pet_friendly=True,
            smoking=False
        )
    ]
    
    print("🔍 Generating roommate and apartment recommendations...")
    recommendations = matcher.generate_recommendations(roommates)
    
    print(f"\n📊 Summary:")
    print(f"   - {recommendations['summary']['total_roommates']} roommates")
    print(f"   - {recommendations['summary']['total_apartments']} apartments")
    print(f"   - {recommendations['summary']['total_restaurants']} restaurants")
    print(f"   - {recommendations['summary']['total_amenities']} amenities")
    
    print(f"\n👥 Roommate Matches: {len(recommendations['roommate_matches'])}")
    for match in recommendations['roommate_matches']:
        print(f"   - {match['roommate1']['name']} & {match['roommate2']['name']}: {match['compatibility_percentage']}% compatible")
    
    print(f"\n🏠 Apartment Matches:")
    for email, matches in recommendations['apartment_matches'].items():
        roommate_name = next(r.name for r in roommates if r.email == email)
        print(f"\n   {roommate_name}:")
        for match in matches[:3]:  # Show top 3
            print(f"     - {match['apartment_name']}: {match['match_percentage']}% match")
            print(f"       Price: {match['price']}, Distance: {match['distance_to_vt']} miles")
    
    # Save recommendations to file
    with open('roommate_recommendations.json', 'w') as f:
        json.dump(recommendations, f, indent=2)
    
    print(f"\n💾 Saved recommendations to roommate_recommendations.json")

if __name__ == "__main__":
    main()
