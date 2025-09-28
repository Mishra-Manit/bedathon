#!/usr/bin/env python3
"""
Test script for the roommate matching API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_roommate():
    """Test creating a roommate profile"""
    print("🧪 Testing roommate profile creation...")
    
    roommate_data = {
        "name": "Alice Johnson",
        "email": "alice@vt.edu",
        "budget_min": 800,
        "budget_max": 1200,
        "preferred_bedrooms": 2,
        "cleanliness": "HIGH",
        "noise_level": "LOW",
        "study_time": "VERY_HIGH",
        "social_level": "MEDIUM",
        "sleep_schedule": "HIGH",
        "pet_friendly": True,
        "smoking": False
    }
    
    response = requests.post(f"{BASE_URL}/matching/roommate-preferences", json=roommate_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_get_roommates():
    """Test getting all roommates"""
    print("\n🧪 Testing get all roommates...")
    
    response = requests.get(f"{BASE_URL}/matching/roommate-preferences")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_find_matches():
    """Test finding roommate matches"""
    print("\n🧪 Testing roommate matching...")
    
    match_data = {
        "min_compatibility": 0.5
    }
    
    response = requests.post(f"{BASE_URL}/matching/roommate-matches", json=match_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_apartment_matches():
    """Test finding apartment matches"""
    print("\n🧪 Testing apartment matching...")
    
    response = requests.get(f"{BASE_URL}/matching/apartment-matches/alice@vt.edu")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_data_summary():
    """Test getting data summary"""
    print("\n🧪 Testing data summary...")
    
    response = requests.get(f"{BASE_URL}/matching/data-summary")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("🚀 Starting roommate matching API tests...")
    
    tests = [
        ("Create Roommate", test_create_roommate),
        ("Get Roommates", test_get_roommates),
        ("Find Matches", test_find_matches),
        ("Apartment Matches", test_apartment_matches),
        ("Data Summary", test_data_summary)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print(f"\n📊 Test Results:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()
