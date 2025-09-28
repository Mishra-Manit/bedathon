#!/usr/bin/env python3
"""
Import apartment data from Virginia Tech Parents Facebook Group spreadsheet
and remove any apartments that mention "2024"
"""

import json
import os
from typing import List, Dict, Any, Optional

def parse_apartment_from_row(row_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Parse apartment data from spreadsheet row"""
    
    # Skip if apartment name contains "2024"
    name = row_data.get('Apartment Complex', '').strip()
    if '2024' in name or 'As of 10/11/2024' in name or 'As of 12/12/2024' in name or 'As of 9/14/2024' in name:
        return None
    
    # Skip if notes contain "2024"
    notes = row_data.get('Notes', '').strip()
    if '2024' in notes:
        return None
    
    # Skip empty names
    if not name or name == 'Apartment Complex':
        return None
    
    # Parse pricing
    def parse_price(price_str: str) -> Optional[str]:
        if not price_str or price_str == 'X' or price_str.strip() == '':
            return None
        return price_str.strip()
    
    # Parse distance
    def parse_distance(dist_str: str) -> Optional[float]:
        if not dist_str or dist_str.strip() == '':
            return None
        try:
            return float(dist_str.strip())
        except:
            return None
    
    # Parse utilities
    def parse_utilities(util_str: str) -> List[str]:
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
    
    # Parse amenities
    def parse_amenities(row: Dict[str, str]) -> List[str]:
        amenities = []
        
        # Pet friendly
        if row.get('Pets?', '').strip().lower() == 'yes':
            amenities.append('Pet Friendly')
        
        # Parking
        parking = row.get('Parking Included', '').strip()
        if parking and parking.lower() != 'no':
            amenities.append('Parking')
        
        # Laundry
        laundry = row.get('Laundry', '').strip()
        if laundry and laundry.lower() != 'no':
            amenities.append('Laundry')
        
        # Furniture
        furniture = row.get('Furniture Included', '').strip()
        if furniture and furniture.lower() == 'yes':
            amenities.append('Furnished')
        
        # Check for pool in name or notes
        name_lower = name.lower()
        if 'pool' in name_lower or 'aqua' in name_lower:
            amenities.append('Pool')
        
        # Check for fitness/gym
        if 'fitness' in name_lower or 'gym' in name_lower or 'health' in name_lower:
            amenities.append('Fitness Center')
        
        return amenities
    
    # Build apartment object
    apartment = {
        'name': name,
        'address': row_data.get('Address', '').strip() or None,
        'studio_price': parse_price(row_data.get('Studio Cost', '')),
        'one_bedroom_price': parse_price(row_data.get('I BDRM Cost', '')),
        'two_bedroom_price': parse_price(row_data.get('2 BDRM Cost', '')),
        'three_bedroom_price': parse_price(row_data.get('3 BDRM Cost', '')),
        'four_bedroom_price': parse_price(row_data.get('4 BDRM Cost', '')),
        'five_bedroom_price': parse_price(row_data.get('5 BDRM Cost', '')),
        'distance_to_vt': parse_distance(row_data.get('Dist to Burruss', '')),
        'amenities': parse_amenities(row_data),
        'pet_friendly': row_data.get('Pets?', '').strip().lower() == 'yes',
        'parking': 'Free' if row_data.get('Parking Included', '').strip().lower() == 'yes' else 'Not included',
        'gym': 'Fitness Center' in parse_amenities(row_data),
        'pool': 'Pool' in parse_amenities(row_data),
        'laundry': row_data.get('Laundry', '').strip() or 'Not specified',
        'wifi_included': 'Internet' in parse_utilities(row_data.get('Utilities Included', '')),
        'utilities_included': parse_utilities(row_data.get('Utilities Included', '')),
        'bus_stop_nearby': row_data.get('Bus Stop', '').strip().lower() == 'yes',
        'phone': row_data.get('Phone Number', '').strip() or None,
        'website': None,
        'description': row_data.get('Notes', '').strip() or None
    }
    
    return apartment

# Sample apartment data from the Google Sheets (manually extracted)
apartments_data = [
    {
        "Apartment Complex": "Alight Blacksburg [was The Village] (As of 3/18/2025)",
        "Phone Number": "540-953-1800",
        "Notes": "*TIERED PRICING*",
        "Lease Term": "12",
        "Lease Type": "Individual",
        "Studio Cost": "X",
        "I BDRM Cost": "X",
        "2 BDRM Cost": "879-979",
        "3 BDRM Cost": "X",
        "4 BDRM Cost": "809",
        "5 BDRM Cost": "X",
        "App Fee": "0",
        "Security Deposit": "none",
        "Pets?": "No",
        "Parking Included": "Yes",
        "Furniture Included": "Yes",
        "Utilities Included": "N",
        "Laundry": "In Unit",
        "Additional Fees": "155 yr",
        "Dist to Burruss": "1.7",
        "Bus Stop": "Yes",
        "Address": "1600 Patrick Henry Drive"
    },
    {
        "Apartment Complex": "Apartment Heights (Price Real Estate) (As of 3/18/2025)",
        "Phone Number": "540-552-1065",
        "Notes": "",
        "Lease Term": "12",
        "Lease Type": "Joint",
        "Studio Cost": "X",
        "I BDRM Cost": "1100-1200",
        "2 BDRM Cost": "1050-1300",
        "3 BDRM Cost": "1920",
        "4 BDRM Cost": "X",
        "5 BDRM Cost": "X",
        "App Fee": "40",
        "Security Deposit": "1 month",
        "Pets?": "Some",
        "Parking Included": "Yes",
        "Furniture Included": "No",
        "Utilities Included": "Varies",
        "Laundry": "On Site",
        "Additional Fees": "",
        "Dist to Burruss": "1.1",
        "Bus Stop": "Yes",
        "Address": "309 Apartment Heights Dr"
    },
    {
        "Apartment Complex": "Apartment Heights Townhomes (Price Real Estate)",
        "Phone Number": "540-552-1065",
        "Notes": "Above Incld.",
        "Lease Term": "12",
        "Lease Type": "Joint",
        "Studio Cost": "X",
        "I BDRM Cost": "X",
        "2 BDRM Cost": "914-1120",
        "3 BDRM Cost": "1596",
        "4 BDRM Cost": "X",
        "5 BDRM Cost": "X",
        "App Fee": "40",
        "Security Deposit": "1 month",
        "Pets?": "Yes",
        "Parking Included": "HT/some N",
        "Furniture Included": "Varies",
        "Utilities Included": "1.1",
        "Laundry": "Yes",
        "Additional Fees": "",
        "Dist to Burruss": "1.1",
        "Bus Stop": "Yes",
        "Address": "309 Apartment Heights Dr"
    },
    {
        "Apartment Complex": "Northview Apartments (TNT Mgmt)",
        "Phone Number": "540-951-1075",
        "Notes": "",
        "Lease Term": "12",
        "Lease Type": "Joint",
        "Studio Cost": "600",
        "I BDRM Cost": "925-970",
        "2 BDRM Cost": "1055-1125",
        "3 BDRM Cost": "1385",
        "4 BDRM Cost": "X",
        "5 BDRM Cost": "X",
        "App Fee": "50",
        "Security Deposit": "1 month",
        "Pets?": "Yes",
        "Parking Included": "No",
        "Furniture Included": "STW",
        "Utilities Included": "On Site",
        "Laundry": "1.2",
        "Additional Fees": "",
        "Dist to Burruss": "1.2",
        "Bus Stop": "Yes",
        "Address": "110 Northview Dr"
    },
    {
        "Apartment Complex": "McDonald St (TNT Property Mgmt/Pointe West)",
        "Phone Number": "951-1075/953-1341",
        "Notes": "",
        "Lease Term": "12",
        "Lease Type": "Joint",
        "Studio Cost": "X",
        "I BDRM Cost": "X",
        "2 BDRM Cost": "1615-1680",
        "3 BDRM Cost": "1965",
        "4 BDRM Cost": "X",
        "5 BDRM Cost": "X",
        "App Fee": "49",
        "Security Deposit": "1 month",
        "Pets?": "Yes",
        "Parking Included": "Yes",
        "Furniture Included": "No",
        "Utilities Included": "ISTW",
        "Laundry": "In Unit",
        "Additional Fees": "",
        "Dist to Burruss": "1",
        "Bus Stop": "Yes",
        "Address": "300 McDonald Street"
    },
    {
        "Apartment Complex": "The Mill (As of 12/12/2024)",
        "Phone Number": "540-552-4272",
        "Notes": "*TIERED PRICING*",
        "Lease Term": "12",
        "Lease Type": "Joint",
        "Studio Cost": "X",
        "I BDRM Cost": "1020+",
        "2 BDRM Cost": "1210+",
        "3 BDRM Cost": "1605+",
        "4 BDRM Cost": "X",
        "5 BDRM Cost": "X",
        "App Fee": "35",
        "Security Deposit": "700-900",
        "Pets?": "Yes",
        "Parking Included": "Yes",
        "Furniture Included": "No",
        "Utilities Included": "RSTW",
        "Laundry": "On Site",
        "Additional Fees": "",
        "Dist to Burruss": "2.4",
        "Bus Stop": "Yes",
        "Address": "1811 Grayland Street"
    }
]

def import_apartments():
    """Import apartments from the data, filtering out 2024 entries"""
    
    apartments = []
    skipped_count = 0
    
    for row in apartments_data:
        apartment = parse_apartment_from_row(row)
        if apartment:
            apartments.append(apartment)
        else:
            skipped_count += 1
    
    print(f"✅ Imported {len(apartments)} apartments")
    print(f"🚫 Skipped {skipped_count} apartments with 2024 references")
    
    # Save to file
    output_file = os.path.join(os.path.dirname(__file__), 'apartments_data.json')
    with open(output_file, 'w') as f:
        json.dump(apartments, f, indent=2)
    
    print(f"💾 Saved to {output_file}")
    
    return apartments

if __name__ == "__main__":
    apartments = import_apartments()
    
    print("\n🏠 Sample apartments:")
    for apt in apartments[:3]:
        print(f"  • {apt['name']} - {apt['two_bedroom_price']} (2BR)")
