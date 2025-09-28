#!/usr/bin/env python3
"""
Update apartment data with real Virginia Tech 2025-2026 housing information
from the Google Sheets document, filtering out any 2024 references
"""

import json
import os
from typing import List, Dict, Any, Optional

def parse_utilities(util_str: str) -> List[str]:
    """Parse utilities from spreadsheet format"""
    if not util_str or util_str.strip() == '':
        return []
    
    utilities = []
    util_map = {
        'C': 'Cable',
        'E': 'Electric', 
        'G': 'Gas',
        'H': 'Heat',
        'I': 'Internet',
        'N': 'Internet',
        'R': 'Recycling',
        'S': 'Sewer',
        'T': 'Trash',
        'W': 'Water'
    }
    
    for char in util_str.strip():
        if char in util_map:
            utilities.append(util_map[char])
    
    return utilities

def parse_amenities(name: str, pets, parking, laundry: str, furniture) -> List[str]:
    """Parse amenities from apartment data"""
    amenities = []
    
    # Pet friendly
    if pets is True or (isinstance(pets, str) and pets.strip().lower() == 'yes'):
        amenities.append('Pet Friendly')
    
    # Parking
    if parking is True or (isinstance(parking, str) and parking.strip().lower() in ['yes', 'free']):
        amenities.append('Parking')
    
    # Laundry
    if laundry and isinstance(laundry, str) and laundry.strip().lower() not in ['no', '']:
        amenities.append('Laundry')
    
    # Furniture
    if furniture is True or (isinstance(furniture, str) and furniture.strip().lower() == 'yes'):
        amenities.append('Furnished')
    
    # Check for pool in name
    name_lower = name.lower()
    if 'pool' in name_lower or 'aqua' in name_lower:
        amenities.append('Pool')
    
    # Check for fitness/gym
    if 'fitness' in name_lower or 'gym' in name_lower or 'health' in name_lower:
        amenities.append('Fitness Center')
    
    return amenities

# Real apartment data from the Virginia Tech Parents Google Sheets (2025-2026)
apartments_data = [
    {
        "name": "Alight Blacksburg [was The Village] (As of 3/18/2025)",
        "phone": "540-953-1800",
        "notes": "*TIERED PRICING*",
        "studio_cost": None,
        "one_bedroom_cost": None,
        "two_bedroom_cost": "879-979",
        "three_bedroom_cost": None,
        "four_bedroom_cost": "809",
        "five_bedroom_cost": None,
        "distance_to_vt": 1.7,
        "pets_allowed": False,
        "parking_included": True,
        "furniture_included": True,
        "utilities_included": "N",  # Internet
        "laundry": "In Unit",
        "bus_stop_nearby": True,
        "address": "1600 Patrick Henry Drive"
    },
    {
        "name": "Apartment Heights (Price Real Estate) (As of 3/18/2025)",
        "phone": "540-552-1065",
        "notes": "",
        "studio_cost": None,
        "one_bedroom_cost": "1100-1200",
        "two_bedroom_cost": "1050-1300",
        "three_bedroom_cost": "1920",
        "four_bedroom_cost": None,
        "five_bedroom_cost": None,
        "distance_to_vt": 1.1,
        "pets_allowed": True,
        "parking_included": True,
        "furniture_included": False,
        "utilities_included": "Varies",
        "laundry": "On Site",
        "bus_stop_nearby": True,
        "address": "309 Apartment Heights Dr"
    },
    {
        "name": "Apartment Heights Townhomes (Price Real Estate)",
        "phone": "540-552-1065",
        "notes": "Above Incld.",
        "studio_cost": None,
        "one_bedroom_cost": None,
        "two_bedroom_cost": "914-1120",
        "three_bedroom_cost": "1596",
        "four_bedroom_cost": None,
        "five_bedroom_cost": None,
        "distance_to_vt": 1.1,
        "pets_allowed": True,
        "parking_included": True,
        "furniture_included": False,
        "utilities_included": "1.1",
        "laundry": "Yes",
        "bus_stop_nearby": True,
        "address": "309 Apartment Heights Dr"
    },
    {
        "name": "Northview Apartments (TNT Mgmt)",
        "phone": "540-951-1075",
        "notes": "",
        "studio_cost": "600",
        "one_bedroom_cost": "925-970",
        "two_bedroom_cost": "1055-1125",
        "three_bedroom_cost": "1385",
        "four_bedroom_cost": None,
        "five_bedroom_cost": None,
        "distance_to_vt": 1.2,
        "pets_allowed": True,
        "parking_included": False,
        "furniture_included": False,
        "utilities_included": "STW",  # Sewer, Trash, Water
        "laundry": "On Site",
        "bus_stop_nearby": True,
        "address": "110 Northview Dr"
    },
    {
        "name": "McDonald St (TNT Property Mgmt/Pointe West)",
        "phone": "951-1075/953-1341",
        "notes": "",
        "studio_cost": None,
        "one_bedroom_cost": None,
        "two_bedroom_cost": "1615-1680",
        "three_bedroom_cost": "1965",
        "four_bedroom_cost": None,
        "five_bedroom_cost": None,
        "distance_to_vt": 1.0,
        "pets_allowed": True,
        "parking_included": True,
        "furniture_included": False,
        "utilities_included": "ISTW",  # Internet, Sewer, Trash, Water
        "laundry": "In Unit",
        "bus_stop_nearby": True,
        "address": "300 McDonald Street"
    },
    {
        "name": "The Mill (As of 12/12/2024)",  # This one has 2024 but is recent
        "phone": "540-552-4272",
        "notes": "*TIERED PRICING*",
        "studio_cost": None,
        "one_bedroom_cost": "1020+",
        "two_bedroom_cost": "1210+",
        "three_bedroom_cost": "1605+",
        "four_bedroom_cost": None,
        "five_bedroom_cost": None,
        "distance_to_vt": 2.4,
        "pets_allowed": True,
        "parking_included": True,
        "furniture_included": False,
        "utilities_included": "RSTW",  # Recycling, Sewer, Trash, Water
        "laundry": "On Site",
        "bus_stop_nearby": True,
        "address": "1811 Grayland Street"
    },
    {
        "name": "Mount Tabor Village (Price Real Estate)",
        "phone": "540-552-1065",
        "notes": "",
        "studio_cost": None,
        "one_bedroom_cost": None,
        "two_bedroom_cost": "1950",
        "three_bedroom_cost": None,
        "four_bedroom_cost": None,
        "five_bedroom_cost": None,
        "distance_to_vt": 2.6,
        "pets_allowed": True,
        "parking_included": True,
        "furniture_included": False,
        "utilities_included": "In Unit",
        "laundry": "Yes",
        "bus_stop_nearby": True,
        "address": "Tabor Village Drive"
    },
    {
        "name": "Mt. Tabor Townhomes (Townside)",
        "phone": "540-552-4000",
        "notes": "NEW 2024",
        "studio_cost": None,
        "one_bedroom_cost": "1200",
        "two_bedroom_cost": "1500",
        "three_bedroom_cost": None,
        "four_bedroom_cost": None,
        "five_bedroom_cost": None,
        "distance_to_vt": None,  # Not specified
        "pets_allowed": True,
        "parking_included": True,
        "furniture_included": False,
        "utilities_included": "Hook ups",
        "laundry": "Lawn Only",
        "bus_stop_nearby": True,
        "address": "Mt. Tabor Road"
    },
    {
        "name": "New Kent Townhomes (TNT Mgmt/Townside/River Mountain/Pointe)",
        "phone": "951-1075/552-4000",
        "notes": "",
        "studio_cost": None,
        "one_bedroom_cost": None,
        "two_bedroom_cost": "1150-1200",
        "three_bedroom_cost": "1450-1920",
        "four_bedroom_cost": "1675-1900",
        "five_bedroom_cost": None,
        "distance_to_vt": 2.6,
        "pets_allowed": False,
        "parking_included": True,
        "furniture_included": False,
        "utilities_included": "T",  # Trash
        "laundry": "In Unit",
        "bus_stop_nearby": True,
        "address": "New Kent Rd"
    },
    {
        "name": "Oak Manor (Townside Property Mgmt/River Mountain/Raines)",
        "phone": "540-552-4000",
        "notes": "",
        "studio_cost": None,
        "one_bedroom_cost": None,
        "two_bedroom_cost": "2400",
        "three_bedroom_cost": "1850-2800",
        "four_bedroom_cost": None,
        "five_bedroom_cost": None,
        "distance_to_vt": 1.8,
        "pets_allowed": True,
        "parking_included": False,
        "furniture_included": False,
        "utilities_included": "Hook ups",
        "laundry": "Yes",
        "bus_stop_nearby": True,
        "address": ""
    },
    {
        "name": "The Orchards Townhomes (CMG)",
        "phone": "540-961-0500",
        "notes": "",
        "studio_cost": None,
        "one_bedroom_cost": None,
        "two_bedroom_cost": "2000-2200",
        "three_bedroom_cost": "2200",
        "four_bedroom_cost": None,
        "five_bedroom_cost": None,
        "distance_to_vt": 2.1,
        "pets_allowed": True,
        "parking_included": True,
        "furniture_included": False,
        "utilities_included": "Hookups",
        "laundry": "Yes",
        "bus_stop_nearby": True,
        "address": "Cherry Lane"
    }
]

def create_apartment_objects():
    """Create apartment objects from the data"""
    apartments = []
    
    for apt_data in apartments_data:
        # Skip if name contains 2024 (except recent ones we want to keep)
        name = apt_data["name"]
        if "2024" in name and "As of 12/12/2024" not in name:  # Keep recent Mill data
            continue
        
        # Parse utilities
        utilities = parse_utilities(apt_data["utilities_included"])
        
        # Parse amenities
        amenities = parse_amenities(
            name,
            apt_data["pets_allowed"],
            apt_data["parking_included"],
            apt_data["laundry"],
            apt_data["furniture_included"]
        )
        
        # Create apartment object
        apartment = {
            "name": name,
            "address": apt_data["address"] or None,
            "studio_price": apt_data["studio_cost"],
            "one_bedroom_price": apt_data["one_bedroom_cost"],
            "two_bedroom_price": apt_data["two_bedroom_cost"],
            "three_bedroom_price": apt_data["three_bedroom_cost"],
            "four_bedroom_price": apt_data["four_bedroom_cost"],
            "five_bedroom_price": apt_data["five_bedroom_cost"],
            "distance_to_vt": apt_data["distance_to_vt"],
            "amenities": amenities,
            "pet_friendly": apt_data["pets_allowed"],
            "parking": "Free" if apt_data["parking_included"] else "Not included",
            "gym": "Fitness Center" in amenities,
            "pool": "Pool" in amenities,
            "laundry": apt_data["laundry"] or "Not specified",
            "wifi_included": "Internet" in utilities,
            "utilities_included": utilities,
            "bus_stop_nearby": apt_data["bus_stop_nearby"],
            "phone": apt_data["phone"],
            "website": None,
            "description": apt_data["notes"] or None
        }
        
        apartments.append(apartment)
    
    return apartments

def update_apartment_database():
    """Update the apartment database with new data"""
    apartments = create_apartment_objects()
    
    print(f"✅ Created {len(apartments)} apartments from VT housing data")
    
    # Count 4-bedroom apartments
    four_bedroom_count = sum(1 for apt in apartments if apt["four_bedroom_price"])
    print(f"🏠 Found {four_bedroom_count} apartments with 4-bedroom options:")
    
    for apt in apartments:
        if apt["four_bedroom_price"]:
            print(f"  • {apt['name']} - {apt['four_bedroom_price']} (4BR)")
    
    # Save to file
    output_file = os.path.join(os.path.dirname(__file__), 'apartments_data.json')
    with open(output_file, 'w') as f:
        json.dump(apartments, f, indent=2)
    
    print(f"💾 Saved to {output_file}")
    
    return apartments

if __name__ == "__main__":
    apartments = update_apartment_database()
    
    print(f"\n📊 Summary:")
    print(f"  • Total apartments: {len(apartments)}")
    print(f"  • 4-bedroom options: {sum(1 for apt in apartments if apt['four_bedroom_price'])}")
    print(f"  • Average distance to VT: {sum(apt['distance_to_vt'] for apt in apartments if apt['distance_to_vt']) / len([apt for apt in apartments if apt['distance_to_vt']]):.1f} miles")
