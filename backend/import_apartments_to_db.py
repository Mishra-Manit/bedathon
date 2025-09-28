#!/usr/bin/env python3
"""
Import apartment data from apartments_data.json into the Supabase database
"""

import json
import os
from sqlmodel import Session, create_engine, select
from models import ApartmentComplex, ApartmentComplexCreate
from dotenv import load_dotenv

load_dotenv()

def import_apartments():
    """Import apartments from JSON file to database"""
    
    # Use SQLite for now to avoid Supabase connection issues
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bedathon.db")
    
    print(f"🔧 Using database: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    
    # Load apartment data from JSON file
    json_file = os.path.join(os.path.dirname(__file__), 'apartments_data.json')
    with open(json_file, 'r') as f:
        apartments_data = json.load(f)
    
    print(f"📊 Loaded {len(apartments_data)} apartments from JSON file")
    
    with Session(engine) as session:
        # Clear existing apartments
        existing_apartments = session.exec(select(ApartmentComplex)).all()
        for apt in existing_apartments:
            session.delete(apt)
        session.commit()
        print("🗑️  Cleared existing apartments")
        
        imported_count = 0
        
        for apt_data in apartments_data:
            try:
                # Parse utilities
                utilities_str = json.dumps(apt_data.get('utilities_included', []))
                
                # Create apartment object
                apartment = ApartmentComplexCreate(
                    name=apt_data['name'],
                    phone_number=apt_data.get('phone'),
                    notes=apt_data.get('description'),
                    lease_term=12,  # Default to 12 months
                    lease_type="Joint",  # Default
                    studio_cost=apt_data.get('studio_price'),
                    one_bedroom_cost=apt_data.get('one_bedroom_price'),
                    two_bedroom_cost=apt_data.get('two_bedroom_price'),
                    three_bedroom_cost=apt_data.get('three_bedroom_price'),
                    four_bedroom_cost=apt_data.get('four_bedroom_price'),
                    five_bedroom_cost=apt_data.get('five_bedroom_cost'),
                    application_fee=None,  # Not in our data
                    security_deposit=None,  # Not in our data
                    pets_allowed=apt_data.get('pet_friendly', False),
                    parking_included=apt_data.get('parking') == 'Free',
                    furniture_included='Furnished' in apt_data.get('amenities', []),
                    utilities_included=utilities_str,
                    laundry=apt_data.get('laundry'),
                    additional_fees=None,  # Not in our data
                    distance_to_burruss=apt_data.get('distance_to_vt'),
                    bus_stop_nearby=apt_data.get('bus_stop_nearby', False),
                    address=apt_data.get('address'),
                    image_url=None  # We'll add images later
                )
                
                # Add to database
                db_apartment = ApartmentComplex.model_validate(apartment)
                session.add(db_apartment)
                imported_count += 1
                
            except Exception as e:
                print(f"⚠️  Error importing {apt_data.get('name', 'Unknown')}: {e}")
        
        session.commit()
        print(f"✅ Successfully imported {imported_count} apartments")
        
        # Count 4-bedroom apartments
        four_bedroom_count = session.exec(
            select(ApartmentComplex).where(ApartmentComplex.four_bedroom_cost.is_not(None))
        ).all()
        
        print(f"🏠 Found {len(four_bedroom_count)} apartments with 4-bedroom options:")
        for apt in four_bedroom_count:
            print(f"  • {apt.name} - {apt.four_bedroom_cost} (4BR)")

if __name__ == "__main__":
    import_apartments()
