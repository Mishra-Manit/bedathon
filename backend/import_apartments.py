#!/usr/bin/env python3
"""
Script to import apartment data from the Virginia Tech Parents Facebook Group spreadsheet.
This script parses the data and imports it into the database.
"""

import re
import json
from typing import Optional, Dict, Any
from sqlmodel import Session, create_engine, select
from models import ApartmentComplex, ApartmentComplexCreate
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bedathon.db")
engine = create_engine(DATABASE_URL)

def parse_cost(cost_str: str) -> Optional[str]:
    """Parse cost string and return cleaned version."""
    if not cost_str or cost_str.strip() in ['X', 'x', '', 'None']:
        return None
    return cost_str.strip()

def parse_boolean(value: str) -> Optional[bool]:
    """Parse boolean values from string."""
    if not value or value.strip() in ['X', 'x', '', 'None']:
        return None
    value = value.strip().lower()
    if value in ['yes', 'y', 'true', '1']:
        return True
    elif value in ['no', 'n', 'false', '0']:
        return False
    return None

def parse_number(value: str) -> Optional[float]:
    """Parse numeric values from string."""
    if not value or value.strip() in ['X', 'x', '', 'None', '?']:
        return None
    try:
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', value.strip())
        return float(cleaned) if cleaned else None
    except (ValueError, TypeError):
        return None

def parse_lease_term(term_str: str) -> Optional[int]:
    """Parse lease term from string."""
    if not term_str or term_str.strip() in ['X', 'x', '', 'None']:
        return None
    # Extract numbers from string like "12", "6,9,12", "11.5"
    numbers = re.findall(r'\d+(?:\.\d+)?', term_str)
    if numbers:
        # Return the first number as integer (most common term)
        return int(float(numbers[0]))
    return None

def parse_utilities(utilities_str: str) -> Optional[str]:
    """Parse utilities string and return as JSON."""
    if not utilities_str or utilities_str.strip() in ['X', 'x', '', 'None']:
        return None
    
    utilities = []
    utility_map = {
        'C': 'Cable',
        'E': 'Electric', 
        'R': 'Recycling',
        'G': 'Gas',
        'T': 'Trash',
        'H': 'Heat',
        'S': 'Sewer',
        'N': 'Internet',
        'W': 'Water'
    }
    
    for char in utilities_str.upper():
        if char in utility_map:
            utilities.append(utility_map[char])
    
    return json.dumps(utilities) if utilities else None

# Raw apartment data from the Google Sheets
APARTMENT_DATA = [
    {
        "name": "Alight Blacksburg [was The Village] (As of 10/11/2024)",
        "phone_number": "540-953-1800",
        "notes": "*TIERED PRICING*",
        "lease_term": "12",
        "lease_type": "Individual",
        "studio_cost": "X",
        "one_bedroom_cost": "X", 
        "two_bedroom_cost": "879-979",
        "three_bedroom_cost": "X",
        "four_bedroom_cost": "779-799",
        "five_bedroom_cost": "X",
        "application_fee": "0",
        "security_deposit": "none",
        "pets_allowed": "No",
        "parking_included": "Yes",
        "furniture_included": "Yes",
        "utilities_included": "N",
        "laundry": "In Unit",
        "additional_fees": "155 yr",
        "distance_to_burruss": "1.7",
        "bus_stop_nearby": "Yes",
        "address": "1600 Patrick Henry Drive"
    },
    {
        "name": "Alight Blacksburg [was The Village] (As of 3/18/2025)",
        "phone_number": "540-953-1800",
        "notes": "*TIERED PRICING*",
        "lease_term": "12",
        "lease_type": "Individual",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "879-979", 
        "three_bedroom_cost": "X",
        "four_bedroom_cost": "809",
        "five_bedroom_cost": "X",
        "application_fee": "0",
        "security_deposit": "none",
        "pets_allowed": "No",
        "parking_included": "Yes",
        "furniture_included": "Yes",
        "utilities_included": "N",
        "laundry": "In Unit",
        "additional_fees": "155 yr",
        "distance_to_burruss": "1.7",
        "bus_stop_nearby": "Yes",
        "address": "1600 Patrick Henry Drive"
    },
    {
        "name": "Apartment Heights (Price Real Estate) (As of 3/18/2025)",
        "phone_number": "540-552-1065",
        "notes": "12",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "1100-1200",
        "two_bedroom_cost": "1050-1300",
        "three_bedroom_cost": "1920",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "40",
        "security_deposit": "1 month",
        "pets_allowed": "Some",
        "parking_included": "Yes",
        "furniture_included": "No",
        "utilities_included": "Varies",
        "laundry": "On Site",
        "additional_fees": "",
        "distance_to_burruss": "1.1",
        "bus_stop_nearby": "Yes",
        "address": "309 Apartment Heights Dr"
    },
    {
        "name": "Apartment Heights Townhomes (Price Real Estate)",
        "phone_number": "540-552-1065",
        "notes": "Above Incld.",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "914-1120",
        "three_bedroom_cost": "1596",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "40",
        "security_deposit": "1 month",
        "pets_allowed": "Yes",
        "parking_included": "HT/some N",
        "furniture_included": "Varies",
        "utilities_included": "1.1",
        "laundry": "Yes",
        "additional_fees": "",
        "distance_to_burruss": "1.1",
        "bus_stop_nearby": "Yes",
        "address": "309 Apartment Heights Dr"
    },
    {
        "name": "Arbors Apartments (Sentinel Properties) (As pf 12/12/2024)",
        "phone_number": "540-552-7425",
        "notes": "SHORT TERM LEASE",
        "lease_term": "6,9,12",
        "lease_type": "Joint",
        "studio_cost": "630-700",
        "one_bedroom_cost": "750-820",
        "two_bedroom_cost": "X",
        "three_bedroom_cost": "900-1050",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "35",
        "security_deposit": "300",
        "pets_allowed": "ESW",
        "parking_included": "On Site",
        "furniture_included": "",
        "utilities_included": "4.3",
        "laundry": "Yes",
        "additional_fees": "",
        "distance_to_burruss": "4.3",
        "bus_stop_nearby": "Yes",
        "address": "777 Triangle Street & South Main Street"
    },
    {
        "name": "The Mill (As of 9/14/2024)",
        "phone_number": "540-552-4272",
        "notes": "*TIERED PRICING*",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "950+",
        "two_bedroom_cost": "1130+",
        "three_bedroom_cost": "1497+",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "35",
        "security_deposit": "600-900",
        "pets_allowed": "Yes",
        "parking_included": "Yes",
        "furniture_included": "No",
        "utilities_included": "RSTW",
        "laundry": "On Site",
        "additional_fees": "",
        "distance_to_burruss": "2.4",
        "bus_stop_nearby": "Yes",
        "address": "1811 Grayland Street"
    },
    {
        "name": "The Mill (As of 12/12/2024)",
        "phone_number": "540-552-4272",
        "notes": "*TIERED PRICING*",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "1020+",
        "two_bedroom_cost": "1210+",
        "three_bedroom_cost": "1605+",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "35",
        "security_deposit": "700-900",
        "pets_allowed": "Yes",
        "parking_included": "Yes",
        "furniture_included": "No",
        "utilities_included": "RSTW",
        "laundry": "On Site",
        "additional_fees": "",
        "distance_to_burruss": "2.4",
        "bus_stop_nearby": "Yes",
        "address": "1811 Grayland Street"
    },
    {
        "name": "Maple Ridge Townhomes (Coastal Ridge RE) As of 12/12/2024",
        "phone_number": "540-870-0505",
        "notes": "*TIERED PRICING*",
        "lease_term": "11.5",
        "lease_type": "Individual",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "925-995",
        "three_bedroom_cost": "930-995",
        "four_bedroom_cost": "895-925",
        "five_bedroom_cost": "X",
        "application_fee": "0",
        "security_deposit": "?",
        "pets_allowed": "No",
        "parking_included": "$",
        "furniture_included": "None",
        "utilities_included": "Yes",
        "laundry": "2.3",
        "additional_fees": "",
        "distance_to_burruss": "2.3",
        "bus_stop_nearby": "Yes",
        "address": "344 Red Maple Drive"
    },
    {
        "name": "Maple Ridge Townhomes (Coastal Ridge RE) As of 3/18/2025",
        "phone_number": "540-870-0505",
        "notes": "*TIERED PRICING*",
        "lease_term": "11.5",
        "lease_type": "Individual",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "935-995",
        "three_bedroom_cost": "930-995",
        "four_bedroom_cost": "895-935",
        "five_bedroom_cost": "X",
        "application_fee": "0",
        "security_deposit": "?",
        "pets_allowed": "No",
        "parking_included": "$",
        "furniture_included": "None",
        "utilities_included": "Yes",
        "laundry": "2.3",
        "additional_fees": "",
        "distance_to_burruss": "2.3",
        "bus_stop_nearby": "Yes",
        "address": "344 Red Maple Drive"
    },
    {
        "name": "Maple Ridge Townhomes (Coastal Ridge RE) As of 7/9/2025",
        "phone_number": "540-870-0505",
        "notes": "*TIERED PRICING*",
        "lease_term": "11.5",
        "lease_type": "Individual",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "945-1005",
        "three_bedroom_cost": "940-1015",
        "four_bedroom_cost": "910-935",
        "five_bedroom_cost": "X",
        "application_fee": "0",
        "security_deposit": "?",
        "pets_allowed": "No",
        "parking_included": "$",
        "furniture_included": "None",
        "utilities_included": "Yes",
        "laundry": "2.3",
        "additional_fees": "",
        "distance_to_burruss": "2.3",
        "bus_stop_nearby": "Yes",
        "address": "344 Red Maple Drive"
    },
    {
        "name": "McDonald St (TNT Property Mgmt/Pointe West)",
        "phone_number": "951-1075/953-1341",
        "notes": "12",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "1615-1680",
        "three_bedroom_cost": "1965",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "49",
        "security_deposit": "1 month",
        "pets_allowed": "Yes",
        "parking_included": "Yes",
        "furniture_included": "No",
        "utilities_included": "ISTW",
        "laundry": "In Unit",
        "additional_fees": "",
        "distance_to_burruss": "1",
        "bus_stop_nearby": "Yes",
        "address": "300 McDonald Street"
    },
    {
        "name": "Mount Tabor Village (Price Real Estate)",
        "phone_number": "540-552-1065",
        "notes": "12",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "X",
        "three_bedroom_cost": "1950",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "40",
        "security_deposit": "1 month",
        "pets_allowed": "Yes",
        "parking_included": "Yes",
        "furniture_included": "In Unit",
        "utilities_included": "2.6",
        "laundry": "Yes",
        "additional_fees": "",
        "distance_to_burruss": "2.6",
        "bus_stop_nearby": "Yes",
        "address": "Tabor Village Drive"
    },
    {
        "name": "Mt. Tabor Townhomes (Townside)",
        "phone_number": "540-552-4000",
        "notes": "NEW 2024",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "1200",
        "two_bedroom_cost": "1500",
        "three_bedroom_cost": "",
        "four_bedroom_cost": "",
        "five_bedroom_cost": "",
        "application_fee": "50",
        "security_deposit": "1 month",
        "pets_allowed": "Yes",
        "parking_included": "No",
        "furniture_included": "Lawn Only",
        "utilities_included": "Hook ups",
        "laundry": "",
        "additional_fees": "",
        "distance_to_burruss": "",
        "bus_stop_nearby": "",
        "address": "Mt. Tabor Road"
    },
    {
        "name": "New Kent Townhomes (TNT Mgmt/Townside/River Mountain/Pointe)",
        "phone_number": "951-1075/552-4000",
        "notes": "12",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "1150-1200",
        "three_bedroom_cost": "1450-1920",
        "four_bedroom_cost": "1675-1900",
        "five_bedroom_cost": "X",
        "application_fee": "50",
        "security_deposit": "1 month",
        "pets_allowed": "Varies",
        "parking_included": "No",
        "furniture_included": "T",
        "utilities_included": "In Unit",
        "laundry": "2.6",
        "additional_fees": "",
        "distance_to_burruss": "2.6",
        "bus_stop_nearby": "Yes",
        "address": "New Kent Rd"
    },
    {
        "name": "North Main Street (Townside Property Mgmt)",
        "phone_number": "540-552-4000",
        "notes": "12",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "1400",
        "one_bedroom_cost": "1200-1800",
        "two_bedroom_cost": "2300",
        "three_bedroom_cost": "X",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "65",
        "security_deposit": "1 month",
        "pets_allowed": "No",
        "parking_included": "Limited",
        "furniture_included": "No",
        "utilities_included": "STW",
        "laundry": "In Unit",
        "additional_fees": "",
        "distance_to_burruss": "",
        "bus_stop_nearby": "",
        "address": "420 & 424 North Main Street"
    },
    {
        "name": "North Main St Apts & Townhomes (Pointe West)",
        "phone_number": "540-953-1341",
        "notes": "12",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "1110",
        "two_bedroom_cost": "1250-2400",
        "three_bedroom_cost": "2100-2640",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "45",
        "security_deposit": "1 month",
        "pets_allowed": "",
        "parking_included": "",
        "furniture_included": "",
        "utilities_included": "",
        "laundry": "",
        "additional_fees": "",
        "distance_to_burruss": "",
        "bus_stop_nearby": "",
        "address": ""
    },
    {
        "name": "Northview Apartments (TNT Mgmt)",
        "phone_number": "540-951-1075",
        "notes": "12",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "600",
        "one_bedroom_cost": "925-970",
        "two_bedroom_cost": "1055-1125",
        "three_bedroom_cost": "1385",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "50",
        "security_deposit": "1 month",
        "pets_allowed": "Yes",
        "parking_included": "No",
        "furniture_included": "STW",
        "utilities_included": "On Site",
        "laundry": "1.2",
        "additional_fees": "",
        "distance_to_burruss": "1.2",
        "bus_stop_nearby": "Yes",
        "address": "110 Northview Dr"
    },
    {
        "name": "Oak Manor (Townside Property Mgmt/River Mountain/Raines)",
        "phone_number": "540-552-4000",
        "notes": "12",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "X",
        "three_bedroom_cost": "2400",
        "four_bedroom_cost": "1850-2800",
        "five_bedroom_cost": "X",
        "application_fee": "50",
        "security_deposit": "1 month",
        "pets_allowed": "Yes",
        "parking_included": "No",
        "furniture_included": "Hook ups",
        "utilities_included": "1.8",
        "laundry": "Yes",
        "additional_fees": "",
        "distance_to_burruss": "1.8",
        "bus_stop_nearby": "Yes",
        "address": ""
    },
    {
        "name": "Oak Tree (Pointe West Mgmt)",
        "phone_number": "** SHORT TERM **",
        "notes": "12",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "1200-1550",
        "three_bedroom_cost": "1750-1800",
        "four_bedroom_cost": "1700-1750",
        "five_bedroom_cost": "X",
        "application_fee": "50",
        "security_deposit": "1 month",
        "pets_allowed": "Yes",
        "parking_included": "Yes",
        "furniture_included": "No",
        "utilities_included": "7.7 Driving",
        "laundry": "Hr +",
        "additional_fees": "",
        "distance_to_burruss": "7.7",
        "bus_stop_nearby": "",
        "address": "170 Twig Street, Christiansburg"
    },
    {
        "name": "Odyssey Apartments (Pointe West Mgmt)",
        "phone_number": "540-953-1341",
        "notes": "12",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "1690",
        "three_bedroom_cost": "X",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "50",
        "security_deposit": "1 month",
        "pets_allowed": "Yes",
        "parking_included": "STW",
        "furniture_included": "In Unit",
        "utilities_included": "2.5",
        "laundry": "Yes",
        "additional_fees": "",
        "distance_to_burruss": "2.5",
        "bus_stop_nearby": "Yes",
        "address": "200 Fairfax Rd"
    },
    {
        "name": "The Orchards Townhomes (CMG)",
        "phone_number": "540-961-0500",
        "notes": "12",
        "lease_term": "12",
        "lease_type": "Joint",
        "studio_cost": "X",
        "one_bedroom_cost": "X",
        "two_bedroom_cost": "2000-2200",
        "three_bedroom_cost": "2200",
        "four_bedroom_cost": "X",
        "five_bedroom_cost": "X",
        "application_fee": "",
        "security_deposit": "Yes",
        "pets_allowed": "No",
        "parking_included": "None",
        "furniture_included": "Hookups",
        "utilities_included": "2.1",
        "laundry": "Yes",
        "additional_fees": "",
        "distance_to_burruss": "2.1",
        "bus_stop_nearby": "Yes",
        "address": "Cherry Lane"
    }
]

def import_apartments():
    """Import apartment data into the database."""
    with Session(engine) as session:
        # Clear existing data
        existing_apartments = session.exec(select(ApartmentComplex)).all()
        for apartment in existing_apartments:
            session.delete(apartment)
        session.commit()
        
        imported_count = 0
        
        for apt_data in APARTMENT_DATA:
            try:
                # Parse the data
                apartment = ApartmentComplexCreate(
                    name=apt_data["name"],
                    phone_number=apt_data["phone_number"] if apt_data["phone_number"] not in ["", "** SHORT TERM **"] else None,
                    notes=apt_data["notes"] if apt_data["notes"] not in ["", "12"] else None,
                    lease_term=parse_lease_term(apt_data["lease_term"]),
                    lease_type=apt_data["lease_type"] if apt_data["lease_type"] not in ["", "X"] else None,
                    studio_cost=parse_cost(apt_data["studio_cost"]),
                    one_bedroom_cost=parse_cost(apt_data["one_bedroom_cost"]),
                    two_bedroom_cost=parse_cost(apt_data["two_bedroom_cost"]),
                    three_bedroom_cost=parse_cost(apt_data["three_bedroom_cost"]),
                    four_bedroom_cost=parse_cost(apt_data["four_bedroom_cost"]),
                    five_bedroom_cost=parse_cost(apt_data["five_bedroom_cost"]),
                    application_fee=parse_number(apt_data["application_fee"]),
                    security_deposit=apt_data["security_deposit"] if apt_data["security_deposit"] not in ["", "?", "none"] else None,
                    pets_allowed=parse_boolean(apt_data["pets_allowed"]),
                    parking_included=parse_boolean(apt_data["parking_included"]),
                    furniture_included=parse_boolean(apt_data["furniture_included"]),
                    utilities_included=parse_utilities(apt_data["utilities_included"]),
                    laundry=apt_data["laundry"] if apt_data["laundry"] not in ["", "2.3", "1.1", "4.3", "2.6", "1.8", "2.1", "7.7", "Hr +"] else None,
                    additional_fees=apt_data["additional_fees"] if apt_data["additional_fees"] not in ["", "155 yr"] else None,
                    distance_to_burruss=parse_number(apt_data["distance_to_burruss"]),
                    bus_stop_nearby=parse_boolean(apt_data["bus_stop_nearby"]),
                    address=apt_data["address"] if apt_data["address"] not in ["", "Cherry Lane"] else None
                )
                
                # Create the apartment record
                db_apartment = ApartmentComplex(**apartment.model_dump())
                session.add(db_apartment)
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing apartment {apt_data.get('name', 'Unknown')}: {e}")
                continue
        
        session.commit()
        print(f"Successfully imported {imported_count} apartment complexes")

if __name__ == "__main__":
    import_apartments()
