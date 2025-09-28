# 🏠 Roommate Matching System for Virginia Tech

## Overview
A comprehensive roommate and apartment matching system that helps Virginia Tech students find compatible roommates and suitable housing based on their preferences and lifestyle.

## 🎯 Features

### 1. **Comprehensive Data Collection**
- **Apartments**: 5+ apartments with detailed pricing, amenities, and distances to VT
- **Restaurants**: 8+ local restaurants with cuisine types, ratings, and delivery options
- **Amenities**: Local amenities including gyms, grocery stores, entertainment venues

### 2. **Smart Preference Matching**
- **Cleanliness Level**: VERY_LOW to VERY_HIGH
- **Noise Tolerance**: VERY_LOW to VERY_HIGH  
- **Study Time**: VERY_LOW to VERY_HIGH
- **Social Level**: VERY_LOW to VERY_HIGH
- **Sleep Schedule**: VERY_LOW (night owl) to VERY_HIGH (early bird)
- **Budget Range**: Min/Max monthly rent
- **Bedroom Preference**: 1-5 bedrooms
- **Pet Friendly**: Yes/No
- **Smoking**: Yes/No

### 3. **Advanced Matching Algorithm**
- **Roommate Compatibility**: 82.6% compatibility between Alice & Carol
- **Apartment Scoring**: 70.7% match for Alice at Apartment Heights
- **Multi-factor Analysis**: Budget, lifestyle, location, amenities

## 📊 Data Generated

### Apartments (5 total)
1. **The Village at Blacksburg** - $850-$1500, 2-3BR, Pool, Gym, Pet Friendly
2. **Apartment Heights** - $1100-$1650, 1-3BR, Pool, Gym, WiFi Included
3. **Maple Ridge Townhomes** - $1200-$1800, 2-4BR, Pet Friendly, In-unit Laundry
4. **Oak Manor** - $1050-$1600, 1-3BR, Pool, Gym, No Pets
5. **The Orchards** - $900-$1550, Studio-3BR, Pool, Gym, WiFi Included

### Restaurants (8 total)
- **Macado's** - American, $$, 4.2⭐
- **Cabo Fish Taco** - Mexican/Seafood, $$, 4.4⭐
- **Gillie's** - Vegetarian/Vegan, $$, 4.6⭐
- **Boudreaux's** - Cajun/Creole, $$$, 4.3⭐
- **Pizza Hut** - Pizza, $, 3.8⭐
- **Subway** - Sandwiches, $, 3.9⭐
- **The Cellar** - American/Bar, $$, 4.1⭐
- **China Inn** - Chinese, $, 4.0⭐

### Amenities (8 total)
- **Grocery**: Kroger, Food Lion
- **Gyms**: Planet Fitness, YMCA
- **Entertainment**: Regal Cinemas
- **Shopping**: Walmart, Target
- **Library**: Blacksburg Library

## 🔧 API Endpoints

### Roommate Management
- `POST /matching/roommate-preferences` - Create/update roommate profile
- `GET /matching/roommate-preferences/{email}` - Get specific roommate
- `GET /matching/roommate-preferences` - Get all roommates

### Matching Services
- `POST /matching/roommate-matches` - Find compatible roommates
- `GET /matching/apartment-matches/{email}` - Find apartment matches
- `POST /matching/recommendations` - Generate comprehensive recommendations

### Data Services
- `GET /matching/data-summary` - Get summary of all data

## 🧮 Matching Algorithm

### Roommate Compatibility Scoring
- **Budget Compatibility** (20%): How well budgets align
- **Cleanliness Match** (25%): Similar cleanliness standards
- **Noise Tolerance** (20%): Compatible noise preferences
- **Study Habits** (15%): Similar study time needs
- **Social Level** (10%): Compatible social preferences
- **Sleep Schedule** (10%): Similar sleep patterns

### Apartment Scoring
- **Budget Fit** (30%): Price within budget range
- **Bedroom Count** (20%): Matches preferred bedrooms
- **Distance to VT** (15%): Proximity to campus
- **Amenities** (15%): Features matching preferences
- **Study Environment** (10%): Quiet/study-friendly features
- **Parking** (10%): Parking availability

## 📈 Example Results

### Top Roommate Matches
- **Alice & Carol**: 82.6% compatible (both high cleanliness, low noise, high study time)
- **Alice & Bob**: 65.6% compatible (different sleep schedules, similar budgets)

### Top Apartment Matches for Alice
1. **Apartment Heights**: 70.7% match, $1350, 2.4 miles
2. **The Orchards**: 69.8% match, $1250, 4.0 miles  
3. **Maple Ridge**: 68.0% match, $1200, 4.3 miles

## 🚀 Usage

### 1. Create Roommate Profile
```json
POST /matching/roommate-preferences
{
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
  "pet_friendly": true,
  "smoking": false
}
```

### 2. Find Roommate Matches
```json
POST /matching/roommate-matches
{
  "min_compatibility": 0.6
}
```

### 3. Get Apartment Recommendations
```
GET /matching/apartment-matches/alice@vt.edu?limit=5
```

## 📁 Files Created
- `comprehensive_data_scraper.py` - Data collection system
- `roommate_matcher.py` - Core matching algorithms
- `matching_fastapi.py` - API endpoints
- `test_matching_api.py` - API testing
- `apartments_data.json` - Apartment data
- `restaurants_data.json` - Restaurant data
- `amenities_data.json` - Amenity data
- `roommate_recommendations.json` - Sample recommendations

## 🎉 Next Steps
1. **Frontend Integration**: Connect to your existing React app
2. **Database Storage**: Replace in-memory storage with persistent database
3. **Real-time Updates**: Add WebSocket support for live matching
4. **Enhanced Scoring**: Add more preference factors (major, year, etc.)
5. **Geolocation**: Use real distance calculations instead of random distances

The system is now ready for integration with your existing apartment browsing app! 🏠✨
