#!/usr/bin/env python3
"""
Migrate all data from local SQLite to Supabase database
"""

import os
import json
from sqlmodel import Session, create_engine, select
from models import ApartmentComplex, Profile
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Local SQLite database
LOCAL_DB_URL = "sqlite:///./bedathon.db"
local_engine = create_engine(LOCAL_DB_URL)

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def migrate_apartments_to_supabase():
    """Migrate all apartments from SQLite to Supabase"""
    print("🏠 Migrating apartments to Supabase...")
    
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get all apartments from local SQLite
    with Session(local_engine) as session:
        apartments = session.exec(select(ApartmentComplex)).all()
    
    print(f"📊 Found {len(apartments)} apartments in local database")
    
    # Prepare apartments for Supabase
    apartments_data = []
    for apt in apartments:
        apartment_dict = {
            "name": apt.name,
            "phone_number": apt.phone_number,
            "notes": apt.notes,
            "lease_term": apt.lease_term,
            "lease_type": apt.lease_type,
            "studio_cost": apt.studio_cost,
            "one_bedroom_cost": apt.one_bedroom_cost,
            "two_bedroom_cost": apt.two_bedroom_cost,
            "three_bedroom_cost": apt.three_bedroom_cost,
            "four_bedroom_cost": apt.four_bedroom_cost,
            "five_bedroom_cost": apt.five_bedroom_cost,
            "application_fee": apt.application_fee,
            "security_deposit": apt.security_deposit,
            "pets_allowed": apt.pets_allowed,
            "parking_included": apt.parking_included,
            "furniture_included": apt.furniture_included,
            "utilities_included": apt.utilities_included,
            "laundry": apt.laundry,
            "additional_fees": apt.additional_fees,
            "distance_to_burruss": apt.distance_to_burruss,
            "bus_stop_nearby": apt.bus_stop_nearby,
            "address": apt.address,
            "image_url": apt.image_url,
            "created_at": apt.created_at.isoformat() if apt.created_at else None,
            "updated_at": apt.updated_at.isoformat() if apt.updated_at else None
        }
        apartments_data.append(apartment_dict)
    
    # Insert apartments into Supabase
    try:
        result = supabase.table("apartmentcomplex").upsert(apartments_data).execute()
        print(f"✅ Successfully migrated {len(apartments_data)} apartments to Supabase")
        return True
    except Exception as e:
        print(f"❌ Error migrating apartments: {e}")
        return False

def migrate_profiles_to_supabase():
    """Migrate all profiles from SQLite to Supabase"""
    print("👥 Migrating profiles to Supabase...")
    
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get all profiles from local SQLite
    with Session(local_engine) as session:
        profiles = session.exec(select(Profile)).all()
    
    print(f"📊 Found {len(profiles)} profiles in local database")
    
    # Prepare profiles for Supabase
    profiles_data = []
    for profile in profiles:
        profile_dict = {
            "name": profile.name,
            "year": profile.year.value if profile.year else None,
            "major": profile.major,
            "budget": profile.budget,
            "move_in": profile.move_in.isoformat() if profile.move_in else None,
            "tags": profile.tags,
            "cleanliness": profile.cleanliness,
            "noise": profile.noise,
            "study_time": profile.study_time,
            "social": profile.social,
            "sleep": profile.sleep,
            "created_at": profile.created_at.isoformat() if profile.created_at else None
        }
        profiles_data.append(profile_dict)
    
    # Insert profiles into Supabase
    try:
        result = supabase.table("profile").upsert(profiles_data).execute()
        print(f"✅ Successfully migrated {len(profiles_data)} profiles to Supabase")
        return True
    except Exception as e:
        print(f"❌ Error migrating profiles: {e}")
        return False

def verify_supabase_data():
    """Verify data was migrated successfully"""
    print("🔍 Verifying Supabase data...")
    
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Check apartments
    apartments_result = supabase.table("apartmentcomplex").select("*").execute()
    print(f"📊 Apartments in Supabase: {len(apartments_result.data)}")
    
    # Check profiles
    profiles_result = supabase.table("profile").select("*").execute()
    print(f"📊 Profiles in Supabase: {len(profiles_result.data)}")
    
    return len(apartments_result.data) > 0 and len(profiles_result.data) > 0

def main():
    print("🚀 STARTING MIGRATION TO SUPABASE")
    print("=" * 50)
    
    # Check if we have Supabase credentials
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials!")
        print("Please check your .env file has SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        return
    
    print(f"📍 Supabase URL: {SUPABASE_URL}")
    
    # Migrate data
    apartments_success = migrate_apartments_to_supabase()
    profiles_success = migrate_profiles_to_supabase()
    
    if apartments_success and profiles_success:
        print("\n🎉 MIGRATION COMPLETE!")
        print("=" * 50)
        
        # Verify migration
        if verify_supabase_data():
            print("✅ All data successfully migrated to Supabase!")
            print("🌐 Your app now uses Supabase as the primary database")
        else:
            print("⚠️ Migration completed but verification failed")
    else:
        print("\n❌ MIGRATION FAILED!")
        print("Please check the errors above and try again")

if __name__ == "__main__":
    main()
