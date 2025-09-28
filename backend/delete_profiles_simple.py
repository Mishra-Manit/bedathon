#!/usr/bin/env python3
"""
Delete specific profiles using the existing database connection
"""

import os
from sqlmodel import Session, create_engine, select, delete
from models import Profile
from dotenv import load_dotenv

load_dotenv()

# Use the same database connection as the backend
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bedathon.db")
engine = create_engine(DATABASE_URL)

def delete_profiles():
    """Delete specified profiles"""
    print("🗑️ DELETING PROFILES...")
    print("=" * 50)
    
    # Profiles to delete
    profiles_to_delete = ["Alice Johnson", "Arjun Puttagunta", "vhyh", "bybu"]
    
    print(f"🎯 Profiles to delete: {', '.join(profiles_to_delete)}")
    print()
    
    with Session(engine) as session:
        # Get all profiles first
        profiles = session.exec(select(Profile)).all()
        print(f"📊 Found {len(profiles)} total profiles")
        
        deleted_count = 0
        
        for profile in profiles:
            if profile.name in profiles_to_delete:
                print(f"🗑️ Deleting: {profile.name} (ID: {profile.id})")
                session.delete(profile)
                deleted_count += 1
        
        # Commit the changes
        session.commit()
        
        print()
        print(f"🎉 DELETION COMPLETE!")
        print(f"✅ Deleted {deleted_count} profiles")
        
        # Show remaining profiles
        remaining_profiles = session.exec(select(Profile)).all()
        print(f"📊 Remaining profiles: {len(remaining_profiles)}")
        
        if remaining_profiles:
            print("👥 Remaining profiles:")
            for profile in remaining_profiles:
                print(f"  • {profile.name}")

if __name__ == "__main__":
    delete_profiles()
