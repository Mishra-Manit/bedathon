#!/usr/bin/env python3
"""
API endpoints for roommate matching system
Integrates with the main Flask app
"""

from flask import Blueprint, request, jsonify
from typing import List, Dict, Any
import json
from roommate_matcher import RoommateMatcher, RoommatePreferences, PreferenceLevel

# Create blueprint for matching endpoints
matching_bp = Blueprint('matching', __name__)

# Initialize the matcher
matcher = RoommateMatcher()

@matching_bp.route('/roommate-preferences', methods=['POST'])
def create_roommate_profile():
    """Create a new roommate profile with preferences"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'budget_min', 'budget_max', 'preferred_bedrooms']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Convert preference levels from strings to enums
        preference_mapping = {
            'VERY_LOW': PreferenceLevel.VERY_LOW,
            'LOW': PreferenceLevel.LOW,
            'MEDIUM': PreferenceLevel.MEDIUM,
            'HIGH': PreferenceLevel.HIGH,
            'VERY_HIGH': PreferenceLevel.VERY_HIGH
        }
        
        roommate = RoommatePreferences(
            name=data['name'],
            email=data['email'],
            budget_min=int(data['budget_min']),
            budget_max=int(data['budget_max']),
            preferred_bedrooms=int(data['preferred_bedrooms']),
            cleanliness=preference_mapping.get(data.get('cleanliness', 'MEDIUM'), PreferenceLevel.MEDIUM),
            noise_level=preference_mapping.get(data.get('noise_level', 'MEDIUM'), PreferenceLevel.MEDIUM),
            study_time=preference_mapping.get(data.get('study_time', 'MEDIUM'), PreferenceLevel.MEDIUM),
            social_level=preference_mapping.get(data.get('social_level', 'MEDIUM'), PreferenceLevel.MEDIUM),
            sleep_schedule=preference_mapping.get(data.get('sleep_schedule', 'MEDIUM'), PreferenceLevel.MEDIUM),
            pet_friendly=data.get('pet_friendly', False),
            smoking=data.get('smoking', False),
            gender_preference=data.get('gender_preference'),
            age_range=tuple(data['age_range']) if data.get('age_range') else None,
            move_in_date=data.get('move_in_date'),
            lease_length=data.get('lease_length')
        )
        
        # For now, store in memory (in production, save to database)
        if not hasattr(matching_bp, 'roommates'):
            matching_bp.roommates = []
        
        # Check if roommate already exists
        existing_roommate = next((r for r in matching_bp.roommates if r.email == roommate.email), None)
        if existing_roommate:
            # Update existing roommate
            index = matching_bp.roommates.index(existing_roommate)
            matching_bp.roommates[index] = roommate
            message = "Roommate profile updated successfully"
        else:
            # Add new roommate
            matching_bp.roommates.append(roommate)
            message = "Roommate profile created successfully"
        
        return jsonify({
            'message': message,
            'roommate': {
                'name': roommate.name,
                'email': roommate.email,
                'budget_min': roommate.budget_min,
                'budget_max': roommate.budget_max,
                'preferred_bedrooms': roommate.preferred_bedrooms
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/roommate-preferences/<email>', methods=['GET'])
def get_roommate_profile(email):
    """Get a roommate profile by email"""
    try:
        if not hasattr(matching_bp, 'roommates'):
            matching_bp.roommates = []
        
        roommate = next((r for r in matching_bp.roommates if r.email == email), None)
        if not roommate:
            return jsonify({'error': 'Roommate not found'}), 404
        
        # Convert to dictionary for JSON response
        roommate_dict = {
            'name': roommate.name,
            'email': roommate.email,
            'budget_min': roommate.budget_min,
            'budget_max': roommate.budget_max,
            'preferred_bedrooms': roommate.preferred_bedrooms,
            'cleanliness': roommate.cleanliness.name,
            'noise_level': roommate.noise_level.name,
            'study_time': roommate.study_time.name,
            'social_level': roommate.social_level.name,
            'sleep_schedule': roommate.sleep_schedule.name,
            'pet_friendly': roommate.pet_friendly,
            'smoking': roommate.smoking,
            'gender_preference': roommate.gender_preference,
            'age_range': list(roommate.age_range) if roommate.age_range else None,
            'move_in_date': roommate.move_in_date,
            'lease_length': roommate.lease_length
        }
        
        return jsonify(roommate_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/roommate-preferences', methods=['GET'])
def get_all_roommate_profiles():
    """Get all roommate profiles"""
    try:
        if not hasattr(matching_bp, 'roommates'):
            matching_bp.roommates = []
        
        roommates_list = []
        for roommate in matching_bp.roommates:
            roommate_dict = {
                'name': roommate.name,
                'email': roommate.email,
                'budget_min': roommate.budget_min,
                'budget_max': roommate.budget_max,
                'preferred_bedrooms': roommate.preferred_bedrooms,
                'cleanliness': roommate.cleanliness.name,
                'noise_level': roommate.noise_level.name,
                'study_time': roommate.study_time.name,
                'social_level': roommate.social_level.name,
                'sleep_schedule': roommate.sleep_schedule.name,
                'pet_friendly': roommate.pet_friendly,
                'smoking': roommate.smoking,
                'gender_preference': roommate.gender_preference,
                'age_range': list(roommate.age_range) if roommate.age_range else None,
                'move_in_date': roommate.move_in_date,
                'lease_length': roommate.lease_length
            }
            roommates_list.append(roommate_dict)
        
        return jsonify({
            'roommates': roommates_list,
            'count': len(roommates_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/roommate-matches', methods=['POST'])
def find_roommate_matches():
    """Find compatible roommate matches"""
    try:
        data = request.get_json()
        min_compatibility = data.get('min_compatibility', 0.6)
        
        if not hasattr(matching_bp, 'roommates'):
            matching_bp.roommates = []
        
        if len(matching_bp.roommates) < 2:
            return jsonify({
                'message': 'Need at least 2 roommates to find matches',
                'matches': []
            }), 200
        
        # Find matches
        matches = matcher.find_roommate_matches(matching_bp.roommates, min_compatibility)
        
        # Format response
        matches_list = []
        for roommate1, roommate2, compatibility in matches:
            matches_list.append({
                'roommate1': {
                    'name': roommate1.name,
                    'email': roommate1.email,
                    'cleanliness': roommate1.cleanliness.name,
                    'noise_level': roommate1.noise_level.name,
                    'study_time': roommate1.study_time.name,
                    'social_level': roommate1.social_level.name,
                    'sleep_schedule': roommate1.sleep_schedule.name,
                    'pet_friendly': roommate1.pet_friendly,
                    'smoking': roommate1.smoking
                },
                'roommate2': {
                    'name': roommate2.name,
                    'email': roommate2.email,
                    'cleanliness': roommate2.cleanliness.name,
                    'noise_level': roommate2.noise_level.name,
                    'study_time': roommate2.study_time.name,
                    'social_level': roommate2.social_level.name,
                    'sleep_schedule': roommate2.sleep_schedule.name,
                    'pet_friendly': roommate2.pet_friendly,
                    'smoking': roommate2.smoking
                },
                'compatibility_score': round(compatibility, 3),
                'compatibility_percentage': round(compatibility * 100, 1)
            })
        
        return jsonify({
            'matches': matches_list,
            'count': len(matches_list),
            'min_compatibility': min_compatibility
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/apartment-matches/<email>', methods=['GET'])
def find_apartment_matches(email):
    """Find apartment matches for a specific roommate"""
    try:
        if not hasattr(matching_bp, 'roommates'):
            matching_bp.roommates = []
        
        roommate = next((r for r in matching_bp.roommates if r.email == email), None)
        if not roommate:
            return jsonify({'error': 'Roommate not found'}), 404
        
        # Find apartment matches
        limit = request.args.get('limit', 5, type=int)
        apartment_matches = matcher.find_apartment_matches(roommate, limit)
        
        # Format response
        matches_list = []
        for match in apartment_matches:
            matches_list.append({
                'apartment_name': match.apartment_name,
                'apartment_address': match.apartment_address,
                'bedroom_count': match.bedroom_count,
                'price': match.price,
                'distance_to_vt': match.distance_to_vt,
                'amenities': match.amenities,
                'match_score': match.match_score,
                'match_percentage': round(match.match_score * 100, 1),
                'reasons': match.reasons,
                'roommate_compatibility': match.roommate_compatibility,
                'apartment_features': match.apartment_features
            })
        
        return jsonify({
            'roommate_email': email,
            'matches': matches_list,
            'count': len(matches_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/recommendations', methods=['POST'])
def generate_recommendations():
    """Generate comprehensive recommendations for all roommates"""
    try:
        if not hasattr(matching_bp, 'roommates'):
            matching_bp.roommates = []
        
        if len(matching_bp.roommates) == 0:
            return jsonify({
                'message': 'No roommates found. Please create roommate profiles first.',
                'recommendations': {
                    'roommate_matches': [],
                    'apartment_matches': {},
                    'summary': {
                        'total_roommates': 0,
                        'total_apartments': len(matcher.apartments),
                        'total_restaurants': len(matcher.restaurants),
                        'total_amenities': len(matcher.amenities)
                    }
                }
            }), 200
        
        # Generate recommendations
        recommendations = matcher.generate_recommendations(matching_bp.roommates)
        
        return jsonify({
            'recommendations': recommendations,
            'generated_at': str(time.time()) if 'time' in globals() else 'now'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/data-summary', methods=['GET'])
def get_data_summary():
    """Get summary of available data"""
    try:
        return jsonify({
            'apartments': {
                'count': len(matcher.apartments),
                'names': [apt['name'] for apt in matcher.apartments]
            },
            'restaurants': {
                'count': len(matcher.restaurants),
                'names': [rest['name'] for rest in matcher.restaurants]
            },
            'amenities': {
                'count': len(matcher.amenities),
                'categories': list(set(amenity['category'] for amenity in matcher.amenities))
            },
            'roommates': {
                'count': len(matching_bp.roommates) if hasattr(matching_bp, 'roommates') else 0,
                'emails': [r.email for r in matching_bp.roommates] if hasattr(matching_bp, 'roommates') else []
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
