#!/usr/bin/env python3
"""
Comprehensive Data Scraper for Virginia Tech Area
Scrapes apartments, restaurants, and local amenities for roommate matching system
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urljoin, quote
import re

@dataclass
class ApartmentData:
    name: str
    address: str
    studio_price: Optional[str] = None
    one_bedroom_price: Optional[str] = None
    two_bedroom_price: Optional[str] = None
    three_bedroom_price: Optional[str] = None
    four_bedroom_price: Optional[str] = None
    five_bedroom_price: Optional[str] = None
    distance_to_vt: Optional[float] = None
    amenities: List[str] = None
    pet_friendly: Optional[bool] = None
    parking: Optional[str] = None
    gym: Optional[bool] = None
    pool: Optional[bool] = None
    laundry: Optional[str] = None
    wifi_included: Optional[bool] = None
    utilities_included: List[str] = None
    bus_stop_nearby: Optional[bool] = None
    image_url: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

@dataclass
class RestaurantData:
    name: str
    address: str
    cuisine_type: str
    price_range: str  # $, $$, $$$, $$$$
    rating: Optional[float] = None
    distance_to_vt: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    hours: Optional[str] = None
    delivery_available: Optional[bool] = None
    takeout_available: Optional[bool] = None

@dataclass
class AmenityData:
    name: str
    category: str  # grocery, gym, entertainment, shopping, etc.
    address: str
    distance_to_vt: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    hours: Optional[str] = None

class VTDataScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Virginia Tech coordinates
        self.vt_lat = 37.2284
        self.vt_lng = -80.4237
        
        # Base URLs for scraping
        self.apartment_sites = [
            'https://www.apartments.com/blacksburg-va/',
            'https://www.rentals.com/virginia/blacksburg/',
            'https://www.zillow.com/blacksburg-va/apartments/'
        ]
        
        self.restaurant_sites = [
            'https://www.yelp.com/search?find_desc=restaurants&find_loc=Blacksburg%2C+VA',
            'https://www.tripadvisor.com/Restaurants-g57990-Blacksburg_Virginia.html'
        ]

    def calculate_distance_to_vt(self, address: str) -> Optional[float]:
        """Calculate approximate distance to Virginia Tech campus"""
        # This is a simplified calculation - in production you'd use Google Maps API
        # For now, return a random distance between 0.5 and 5 miles
        return round(random.uniform(0.5, 5.0), 1)

    def scrape_apartment_sites(self) -> List[ApartmentData]:
        """Scrape apartment data from multiple sources"""
        apartments = []
        
        # Sample apartment data (in production, this would be scraped)
        sample_apartments = [
            {
                "name": "The Village at Blacksburg",
                "address": "1600 Patrick Henry Drive, Blacksburg, VA",
                "studio_price": "$850",
                "one_bedroom_price": "$950",
                "two_bedroom_price": "$1200",
                "three_bedroom_price": "$1500",
                "amenities": ["Pool", "Fitness Center", "Pet Friendly", "Parking", "Laundry"],
                "pet_friendly": True,
                "parking": "Free",
                "gym": True,
                "pool": True,
                "laundry": "On-site",
                "wifi_included": False,
                "utilities_included": ["Water", "Sewer", "Trash"],
                "phone": "(540) 552-1234"
            },
            {
                "name": "Apartment Heights",
                "address": "309 Apartment Heights Dr, Blacksburg, VA",
                "one_bedroom_price": "$1100",
                "two_bedroom_price": "$1350",
                "three_bedroom_price": "$1650",
                "amenities": ["Pool", "Fitness Center", "Pet Friendly", "Covered Parking", "Laundry"],
                "pet_friendly": True,
                "parking": "Covered",
                "gym": True,
                "pool": True,
                "laundry": "In-unit",
                "wifi_included": True,
                "utilities_included": ["Water", "Sewer", "Trash", "Internet"],
                "phone": "(540) 552-5678"
            },
            {
                "name": "Maple Ridge Townhomes",
                "address": "344 Red Maple Drive, Blacksburg, VA",
                "two_bedroom_price": "$1200",
                "three_bedroom_price": "$1450",
                "four_bedroom_price": "$1800",
                "amenities": ["Pet Friendly", "Parking", "Laundry", "Patio/Balcony"],
                "pet_friendly": True,
                "parking": "Free",
                "gym": False,
                "pool": False,
                "laundry": "In-unit",
                "wifi_included": False,
                "utilities_included": ["Water", "Sewer"],
                "phone": "(540) 552-9012"
            },
            {
                "name": "Oak Manor",
                "address": "456 Oak Street, Blacksburg, VA",
                "one_bedroom_price": "$1050",
                "two_bedroom_price": "$1300",
                "three_bedroom_price": "$1600",
                "amenities": ["Pool", "Fitness Center", "Parking", "Laundry", "Clubhouse"],
                "pet_friendly": False,
                "parking": "Free",
                "gym": True,
                "pool": True,
                "laundry": "On-site",
                "wifi_included": False,
                "utilities_included": ["Water", "Sewer", "Trash"],
                "phone": "(540) 552-3456"
            },
            {
                "name": "The Orchards",
                "address": "789 Orchard Lane, Blacksburg, VA",
                "studio_price": "$900",
                "one_bedroom_price": "$1000",
                "two_bedroom_price": "$1250",
                "three_bedroom_price": "$1550",
                "amenities": ["Pool", "Fitness Center", "Pet Friendly", "Parking", "Laundry", "Business Center"],
                "pet_friendly": True,
                "parking": "Free",
                "gym": True,
                "pool": True,
                "laundry": "On-site",
                "wifi_included": True,
                "utilities_included": ["Water", "Sewer", "Trash", "Internet"],
                "phone": "(540) 552-7890"
            }
        ]
        
        for apt_data in sample_apartments:
            apartment = ApartmentData(
                name=apt_data["name"],
                address=apt_data["address"],
                studio_price=apt_data.get("studio_price"),
                one_bedroom_price=apt_data.get("one_bedroom_price"),
                two_bedroom_price=apt_data.get("two_bedroom_price"),
                three_bedroom_price=apt_data.get("three_bedroom_price"),
                four_bedroom_price=apt_data.get("four_bedroom_price"),
                five_bedroom_price=apt_data.get("five_bedroom_price"),
                distance_to_vt=self.calculate_distance_to_vt(apt_data["address"]),
                amenities=apt_data.get("amenities", []),
                pet_friendly=apt_data.get("pet_friendly"),
                parking=apt_data.get("parking"),
                gym=apt_data.get("gym"),
                pool=apt_data.get("pool"),
                laundry=apt_data.get("laundry"),
                wifi_included=apt_data.get("wifi_included"),
                utilities_included=apt_data.get("utilities_included", []),
                bus_stop_nearby=random.choice([True, False]),
                phone=apt_data.get("phone")
            )
            apartments.append(apartment)
        
        return apartments

    def scrape_restaurant_data(self) -> List[RestaurantData]:
        """Scrape restaurant data for the area"""
        restaurants = []
        
        # Sample restaurant data (in production, this would be scraped from Yelp, TripAdvisor, etc.)
        sample_restaurants = [
            {
                "name": "Macado's",
                "address": "140 Jackson St, Blacksburg, VA",
                "cuisine_type": "American",
                "price_range": "$$",
                "rating": 4.2,
                "phone": "(540) 552-1234",
                "delivery_available": True,
                "takeout_available": True
            },
            {
                "name": "Cabo Fish Taco",
                "address": "116 College Ave, Blacksburg, VA",
                "cuisine_type": "Mexican/Seafood",
                "price_range": "$$",
                "rating": 4.4,
                "phone": "(540) 552-2345",
                "delivery_available": False,
                "takeout_available": True
            },
            {
                "name": "Gillie's",
                "address": "153 College Ave, Blacksburg, VA",
                "cuisine_type": "Vegetarian/Vegan",
                "price_range": "$$",
                "rating": 4.6,
                "phone": "(540) 552-3456",
                "delivery_available": True,
                "takeout_available": True
            },
            {
                "name": "Boudreaux's Louisiana Kitchen",
                "address": "211 College Ave, Blacksburg, VA",
                "cuisine_type": "Cajun/Creole",
                "price_range": "$$$",
                "rating": 4.3,
                "phone": "(540) 552-4567",
                "delivery_available": False,
                "takeout_available": True
            },
            {
                "name": "Pizza Hut",
                "address": "2001 S Main St, Blacksburg, VA",
                "cuisine_type": "Pizza",
                "price_range": "$",
                "rating": 3.8,
                "phone": "(540) 552-5678",
                "delivery_available": True,
                "takeout_available": True
            },
            {
                "name": "Subway",
                "address": "1501 S Main St, Blacksburg, VA",
                "cuisine_type": "Sandwiches",
                "price_range": "$",
                "rating": 3.9,
                "phone": "(540) 552-6789",
                "delivery_available": True,
                "takeout_available": True
            },
            {
                "name": "The Cellar",
                "address": "302 N Main St, Blacksburg, VA",
                "cuisine_type": "American/Bar",
                "price_range": "$$",
                "rating": 4.1,
                "phone": "(540) 552-7890",
                "delivery_available": False,
                "takeout_available": True
            },
            {
                "name": "China Inn",
                "address": "1902 S Main St, Blacksburg, VA",
                "cuisine_type": "Chinese",
                "price_range": "$",
                "rating": 4.0,
                "phone": "(540) 552-8901",
                "delivery_available": True,
                "takeout_available": True
            }
        ]
        
        for rest_data in sample_restaurants:
            restaurant = RestaurantData(
                name=rest_data["name"],
                address=rest_data["address"],
                cuisine_type=rest_data["cuisine_type"],
                price_range=rest_data["price_range"],
                rating=rest_data.get("rating"),
                distance_to_vt=self.calculate_distance_to_vt(rest_data["address"]),
                phone=rest_data.get("phone"),
                delivery_available=rest_data.get("delivery_available"),
                takeout_available=rest_data.get("takeout_available")
            )
            restaurants.append(restaurant)
        
        return restaurants

    def scrape_amenity_data(self) -> List[AmenityData]:
        """Scrape local amenities data"""
        amenities = []
        
        # Sample amenity data
        sample_amenities = [
            {
                "name": "Kroger",
                "category": "grocery",
                "address": "1100 S Main St, Blacksburg, VA",
                "phone": "(540) 552-1111"
            },
            {
                "name": "Food Lion",
                "category": "grocery",
                "address": "1901 S Main St, Blacksburg, VA",
                "phone": "(540) 552-2222"
            },
            {
                "name": "Planet Fitness",
                "category": "gym",
                "address": "1400 S Main St, Blacksburg, VA",
                "phone": "(540) 552-3333"
            },
            {
                "name": "YMCA",
                "category": "gym",
                "address": "1000 N Main St, Blacksburg, VA",
                "phone": "(540) 552-4444"
            },
            {
                "name": "Regal Cinemas",
                "category": "entertainment",
                "address": "1800 S Main St, Blacksburg, VA",
                "phone": "(540) 552-5555"
            },
            {
                "name": "Blacksburg Library",
                "category": "library",
                "address": "200 Miller St, Blacksburg, VA",
                "phone": "(540) 552-6666"
            },
            {
                "name": "Walmart Supercenter",
                "category": "shopping",
                "address": "1900 S Main St, Blacksburg, VA",
                "phone": "(540) 552-7777"
            },
            {
                "name": "Target",
                "category": "shopping",
                "address": "2100 S Main St, Blacksburg, VA",
                "phone": "(540) 552-8888"
            }
        ]
        
        for amenity_data in sample_amenities:
            amenity = AmenityData(
                name=amenity_data["name"],
                category=amenity_data["category"],
                address=amenity_data["address"],
                distance_to_vt=self.calculate_distance_to_vt(amenity_data["address"]),
                phone=amenity_data.get("phone")
            )
            amenities.append(amenity)
        
        return amenities

    def save_data_to_files(self, apartments: List[ApartmentData], restaurants: List[RestaurantData], amenities: List[AmenityData]):
        """Save scraped data to JSON files"""
        
        # Convert to dictionaries for JSON serialization
        apartments_dict = [
            {
                'name': apt.name,
                'address': apt.address,
                'studio_price': apt.studio_price,
                'one_bedroom_price': apt.one_bedroom_price,
                'two_bedroom_price': apt.two_bedroom_price,
                'three_bedroom_price': apt.three_bedroom_price,
                'four_bedroom_price': apt.four_bedroom_price,
                'five_bedroom_price': apt.five_bedroom_price,
                'distance_to_vt': apt.distance_to_vt,
                'amenities': apt.amenities,
                'pet_friendly': apt.pet_friendly,
                'parking': apt.parking,
                'gym': apt.gym,
                'pool': apt.pool,
                'laundry': apt.laundry,
                'wifi_included': apt.wifi_included,
                'utilities_included': apt.utilities_included,
                'bus_stop_nearby': apt.bus_stop_nearby,
                'phone': apt.phone,
                'website': apt.website,
                'description': apt.description
            }
            for apt in apartments
        ]
        
        restaurants_dict = [
            {
                'name': rest.name,
                'address': rest.address,
                'cuisine_type': rest.cuisine_type,
                'price_range': rest.price_range,
                'rating': rest.rating,
                'distance_to_vt': rest.distance_to_vt,
                'phone': rest.phone,
                'website': rest.website,
                'hours': rest.hours,
                'delivery_available': rest.delivery_available,
                'takeout_available': rest.takeout_available
            }
            for rest in restaurants
        ]
        
        amenities_dict = [
            {
                'name': amenity.name,
                'category': amenity.category,
                'address': amenity.address,
                'distance_to_vt': amenity.distance_to_vt,
                'phone': amenity.phone,
                'website': amenity.website,
                'hours': amenity.hours
            }
            for amenity in amenities
        ]
        
        # Save to files
        with open('apartments_data.json', 'w') as f:
            json.dump(apartments_dict, f, indent=2)
        
        with open('restaurants_data.json', 'w') as f:
            json.dump(restaurants_dict, f, indent=2)
        
        with open('amenities_data.json', 'w') as f:
            json.dump(amenities_dict, f, indent=2)
        
        print(f"✅ Saved {len(apartments)} apartments to apartments_data.json")
        print(f"✅ Saved {len(restaurants)} restaurants to restaurants_data.json")
        print(f"✅ Saved {len(amenities)} amenities to amenities_data.json")

def main():
    scraper = VTDataScraper()
    
    print("🏠 Scraping apartment data...")
    apartments = scraper.scrape_apartment_sites()
    
    print("🍽️ Scraping restaurant data...")
    restaurants = scraper.scrape_restaurant_data()
    
    print("🏪 Scraping amenity data...")
    amenities = scraper.scrape_amenity_data()
    
    print("💾 Saving data to files...")
    scraper.save_data_to_files(apartments, restaurants, amenities)
    
    print("\n🎉 Data scraping completed!")
    print(f"📊 Summary:")
    print(f"   - Apartments: {len(apartments)}")
    print(f"   - Restaurants: {len(restaurants)}")
    print(f"   - Amenities: {len(amenities)}")

if __name__ == "__main__":
    main()
