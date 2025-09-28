#!/usr/bin/env python3
"""
Add missing columns to Supabase profiles table
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

def add_columns_to_profiles_table():
    """Add missing columns to the profiles table"""
    cfg = get_supabase_config()
    
    if not cfg["url"] or not cfg["api_key"]:
        print("❌ Missing Supabase configuration")
        return
    
    # SQL commands to add the missing columns
    sql_commands = [
        "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS max_distance_to_vt REAL DEFAULT 5.0;",
        "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS preferred_amenities TEXT DEFAULT '[]';"
    ]
    
    for sql in sql_commands:
        try:
            url = f"{cfg['url']}/rest/v1/rpc/exec_sql"
            headers = {
                "apikey": cfg["api_key"],
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            }
            
            payload = {"sql": sql}
            
            resp = httpx.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            
            print(f"✅ Executed: {sql}")
            
        except Exception as e:
            print(f"❌ Failed to execute '{sql}': {e}")
            # Try alternative approach using direct SQL
            try:
                url = f"{cfg['url']}/rest/v1/profiles"
                headers = {
                    "apikey": cfg["api_key"],
                    "Authorization": f"Bearer {cfg['api_key']}",
                    "Content-Type": "application/json",
                }
                
                # Test if columns exist by trying to select them
                resp = httpx.get(f"{url}?select=max_distance_to_vt,preferred_amenities&limit=1", headers=headers)
                if resp.status_code == 200:
                    print("✅ Columns already exist")
                    continue
                else:
                    print(f"⚠️  Columns don't exist, but direct SQL failed: {e}")
                    
            except Exception as e2:
                print(f"❌ Alternative approach also failed: {e2}")

def test_profile_creation():
    """Test creating a profile with the new columns"""
    cfg = get_supabase_config()
    
    test_profile = {
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
        "sleep": 3,
        "max_distance_to_vt": 5.0,
        "preferred_amenities": []
    }
    
    try:
        url = f"{cfg['url']}/rest/v1/profiles"
        headers = {
            "apikey": cfg["api_key"],
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        
        resp = httpx.post(url, headers=headers, json=test_profile, timeout=12)
        resp.raise_for_status()
        
        result = resp.json()
        print("✅ Test profile creation successful!")
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
        print(f"❌ Test profile creation failed: {e}")

if __name__ == "__main__":
    print("🔧 Adding missing columns to Supabase profiles table...")
    add_columns_to_profiles_table()
    
    print("\n🧪 Testing profile creation...")
    test_profile_creation()
