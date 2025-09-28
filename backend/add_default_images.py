#!/usr/bin/env python3
"""
Add default apartment images using Lorem Picsum for reliable placeholder images
"""

import os
from sqlmodel import Session, create_engine, select
from models import ApartmentComplex
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bedathon.db")
engine = create_engine(DATABASE_URL)

def add_default_images():
    """Add default images to all apartments without images"""
    
    with Session(engine) as session:
        apartments = session.exec(select(ApartmentComplex)).all()
        
        print(f"🏠 Found {len(apartments)} apartments")
        
        updated_count = 0
        
        for apartment in apartments:
            if not apartment.image_url:
                # Use Lorem Picsum for reliable placeholder images
                # Different images for variety based on apartment name
                seed = hash(apartment.name) % 1000
                image_url = f"https://picsum.photos/800/600?random={seed}"
                
                apartment.image_url = image_url
                apartment.updated_at = datetime.now(timezone.utc)
                session.add(apartment)
                updated_count += 1
                
                print(f"✅ Added image to: {apartment.name[:50]}...")
            else:
                print(f"⏭️  Already has image: {apartment.name[:50]}...")
        
        session.commit()
        
        print(f"\n🎉 Added default images to {updated_count} apartments!")
        return updated_count

if __name__ == "__main__":
    print("🏠 Adding default apartment images...")
    print("=" * 50)
    
    updated_count = add_default_images()
    
    print(f"\n✅ Complete! Updated {updated_count} apartments")
    print("🌐 All apartments now have images!")
