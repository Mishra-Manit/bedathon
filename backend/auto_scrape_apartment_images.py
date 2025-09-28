#!/usr/bin/env python3
"""
Auto-scrape apartment images from Google search
Searches for each apartment name + "Blacksburg VA" and gets real images
"""

import os
import requests
from bs4 import BeautifulSoup
import time
import random
from sqlmodel import Session, create_engine, select
from models import ApartmentComplex
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bedathon.db")
engine = create_engine(DATABASE_URL)

class ApartmentImageScraper:
    def __init__(self, engine=engine):
        self.engine = engine
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_apartments(self):
        """Get all apartments from database"""
        with Session(self.engine) as session:
            return session.exec(select(ApartmentComplex)).all()
    
    def search_apartment_images(self, apartment_name):
        """Search Google for apartment images"""
        try:
            # Clean apartment name for search
            clean_name = apartment_name.split('(')[0].strip()
            search_query = f"{clean_name} Blacksburg VA apartments"
            
            print(f"🔍 Searching for: {search_query}")
            
            # Use Google Images search
            url = f"https://www.google.com/search?q={search_query}&tbm=isch"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find image URLs in the page
            images = []
            for img in soup.find_all('img')[:10]:  # Get first 10 images
                src = img.get('src')
                if src and src.startswith('http') and 'google' not in src:
                    images.append(src)
            
            return images[:3]  # Return top 3 images
            
        except Exception as e:
            print(f"❌ Error searching for {apartment_name}: {e}")
            return []
    
    def update_apartment_image(self, apartment_id, image_url):
        """Update apartment with new image URL"""
        try:
            with Session(self.engine) as session:
                apartment = session.get(ApartmentComplex, apartment_id)
                if apartment:
                    apartment.image_url = image_url
                    apartment.updated_at = datetime.now(timezone.utc)
                    session.add(apartment)
                    session.commit()
                    session.refresh(apartment)
                    return True
            return False
        except Exception as e:
            print(f"❌ Error updating apartment {apartment_id}: {e}")
            return False
    
    def scrape_all_apartments(self):
        """Scrape images for all apartments"""
        apartments = self.get_apartments()
        print(f"🏠 Found {len(apartments)} apartments to process")
        
        updated_count = 0
        
        for i, apartment in enumerate(apartments, 1):
            print(f"\n[{i}/{len(apartments)}] Processing: {apartment.name}")
            
            # Skip if already has image
            if apartment.image_url:
                print(f"⏭️  Already has image: {apartment.image_url[:50]}...")
                continue
            
            # Search for images
            images = self.search_apartment_images(apartment.name)
            
            if images:
                # Use the first valid image
                image_url = images[0]
                print(f"✅ Found image: {image_url[:80]}...")
                
                # Update database
                if self.update_apartment_image(apartment.id, image_url):
                    print(f"✅ Updated database for {apartment.name}")
                    updated_count += 1
                else:
                    print(f"❌ Failed to update database")
            else:
                print(f"❌ No images found for {apartment.name}")
            
            # Be respectful with delays
            time.sleep(random.uniform(2, 4))
        
        print(f"\n🎉 Scraping complete! Updated {updated_count} apartments with images")
        return updated_count

def main():
    print("🏠 Auto-scraping apartment images from Google...")
    print("=" * 60)
    
    scraper = ApartmentImageScraper()
    updated_count = scraper.scrape_all_apartments()
    
    print(f"\n✅ Process complete!")
    print(f"📊 Updated {updated_count} apartments with real images")
    print(f"🌐 Your apartments now have real images from Google search!")

if __name__ == "__main__":
    main()
