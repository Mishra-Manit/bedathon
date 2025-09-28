#!/usr/bin/env python3
"""
Check the current schema of the Supabase profiles table
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

def get_supabase_config():
    """Get Supabase configuration from environment variables"""
    return {
        "url": os.getenv("SUPABASE_URL"),
        "api_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    }

def check_profiles_schema():
    """Check what columns exist in the profiles table"""
    cfg = get_supabase_config()
    
    try:
        url = f"{cfg['url']}/rest/v1/profiles"
        headers = {
            "apikey": cfg["api_key"],
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        }
        
        # Try to get one profile to see the schema
        resp = httpx.get(f"{url}?limit=1", headers=headers)
        resp.raise_for_status()
        
        result = resp.json()
        if result and len(result) > 0:
            profile = result[0]
            print("📋 Current profiles table schema:")
            for key, value in profile.items():
                print(f"  • {key}: {type(value).__name__} = {value}")
        else:
            print("📋 No profiles found, checking table info...")
            
            # Try to get table info using a different approach
            info_url = f"{cfg['url']}/rest/v1/profiles"
            info_headers = {
                "apikey": cfg["api_key"],
                "Authorization": f"Bearer {cfg['api_key']}",
            }
            
            info_resp = httpx.get(info_url, headers=info_headers)
            print(f"Table response status: {info_resp.status_code}")
            
    except Exception as e:
        print(f"❌ Failed to check schema: {e}")

def test_minimal_profile():
    """Test creating a minimal profile with only known columns"""
    cfg = get_supabase_config()
    
    # Minimal profile with only the basic columns that should exist
    minimal_profile = {
        "name": "Test User",
        "year": "Junior",
        "major": "Computer Science",
        "budget": 1000,
        "move_in": None,
        "tags": [],
        "cleanliness": 3,
        "noise": 3,
        "study_time": 3,
        "social": 3,
        "sleep": 3
    }
    
    try:
        url = f"{cfg['url']}/rest/v1/profiles"
        headers = {
            "apikey": cfg["api_key"],
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        
        resp = httpx.post(url, headers=headers, json=minimal_profile, timeout=12)
        resp.raise_for_status()
        
        result = resp.json()
        print("✅ Minimal profile creation successful!")
        print(f"Created profile: {result}")
        
        # Clean up test profile
        if result and len(result) > 0:
            profile_id = result[0].get('id')
            if profile_id:
                delete_url = f"{url}?id=eq.{profile_id}"
                delete_resp = httpx.delete(delete_url, headers=headers)
                if delete_resp.status_code == 204:
                    print("🧹 Cleaned up test profile")
        
    except Exception as e:
        print(f"❌ Minimal profile creation failed: {e}")

if __name__ == "__main__":
    print("🔍 Checking Supabase profiles table schema...")
    check_profiles_schema()
    
    print("\n🧪 Testing minimal profile creation...")
    test_minimal_profile()
