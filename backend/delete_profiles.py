#!/usr/bin/env python3
"""
Delete specific profiles from Supabase database
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def delete_profiles():
    """Delete specified profiles from Supabase"""
    print("🗑️ DELETING PROFILES FROM SUPABASE...")
    print("=" * 50)
    
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Profiles to delete (by name)
    profiles_to_delete = ["Alice Johnson", "Arjun Puttagunta", "vhyh", "bybu"]
    
    print(f"🎯 Profiles to delete: {', '.join(profiles_to_delete)}")
    print()
    
    # Get all profiles first
    try:
        result = supabase.table("profile").select("*").execute()
        all_profiles = result.data
        print(f"📊 Found {len(all_profiles)} total profiles")
        
        deleted_count = 0
        
        for profile in all_profiles:
            profile_name = profile.get("name", "")
            profile_id = profile.get("id", "")
            
            if profile_name in profiles_to_delete:
                print(f"🗑️ Deleting: {profile_name} (ID: {profile_id})")
                
                # Delete the profile
                delete_result = supabase.table("profile").delete().eq("id", profile_id).execute()
                
                if delete_result.data:
                    print(f"✅ Successfully deleted: {profile_name}")
                    deleted_count += 1
                else:
                    print(f"❌ Failed to delete: {profile_name}")
        
        print()
        print(f"🎉 DELETION COMPLETE!")
        print(f"✅ Deleted {deleted_count} profiles")
        
        # Show remaining profiles
        remaining_result = supabase.table("profile").select("*").execute()
        remaining_profiles = remaining_result.data
        print(f"📊 Remaining profiles: {len(remaining_profiles)}")
        
        if remaining_profiles:
            print("👥 Remaining profiles:")
            for profile in remaining_profiles:
                print(f"  • {profile.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    delete_profiles()
