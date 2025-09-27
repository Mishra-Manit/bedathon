import os
import hashlib
import requests
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlmodel import Session, create_engine, select
from models import ApartmentComplex
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bedathon.db")
engine = create_engine(DATABASE_URL)

class ManualImageInput:
    def __init__(self, engine=engine):
        self.engine = engine
        self.session = requests.Session()

    def get_all_apartments(self) -> List[ApartmentComplex]:
        with Session(self.engine) as session:
            return session.exec(select(ApartmentComplex)).all()

    def update_apartment_image(self, apartment_name: str, image_url: str) -> bool:
        with Session(self.engine) as session:
            # Find apartment by name (case-insensitive partial match)
            apartments = session.exec(select(ApartmentComplex).where(ApartmentComplex.name.ilike(f"%{apartment_name}%"))).all()
            
            if not apartments:
                print(f"❌ Apartment not found: {apartment_name}")
                return False
            
            # If multiple matches, pick the first one or ask for clarification
            apartment = apartments[0] 
            
            apartment.image_url = image_url
            apartment.updated_at = datetime.now(timezone.utc)
            session.add(apartment)
            session.commit()
            session.refresh(apartment)
            return True

    def list_all_apartments(self):
        apartments = self.get_all_apartments()
        print("\n--- Current Apartment Image Status ---")
        for i, apt in enumerate(apartments, 1):
            status = "✅" if apt.image_url else "❌"
            print(f"{status} {i}. {apt.name:<50} | {apt.image_url or 'No image'}")
        print("--------------------------------------")

    def interactive_update(self):
        apartments = self.get_all_apartments()
        print("\n--- Interactive Image Update ---")
        for apt in apartments:
            print(f"\nApartment: {apt.name}")
            print(f"Current image: {apt.image_url or 'No image'}")
            new_url = input("Enter new image URL (or press Enter to skip): ").strip()
            if new_url:
                if self.update_apartment_image(apt.name, new_url):
                    print(f"✅ Updated {apt.name} with image: {new_url}")
                else:
                    print(f"❌ Failed to update {apt.name}")
            else:
                print(f"Skipped {apt.name}")
        print("\n--- Interactive Update Complete ---")

    def bulk_update(self):
        print("\n--- Bulk Image Update ---")
        print("Enter apartment name and image URL pairs, one per line.")
        print("Format: \"Apartment Name\": [Image URL]")
        print("Type 'DONE' on a new line when finished.")
        
        updates = {}
        while True:
            line = input().strip()
            if line.upper() == 'DONE':
                break
            try:
                # Simple parsing for "Name": URL format
                parts = line.split(':', 1)
                if len(parts) == 2:
                    name = parts[0].strip().strip('"')
                    url = parts[1].strip()
                    updates[name] = url
                else:
                    print(f"Invalid format: {line}. Please use \"Apartment Name\": [Image URL]")
            except Exception as e:
                print(f"Error parsing line '{line}': {e}")

        apartments = self.get_all_apartments()
        updated_count = 0
        for apt_name, new_url in updates.items():
            found = False
            for apt in apartments:
                if apt_name.lower() in apt.name.lower(): # Case-insensitive partial match
                    if self.update_apartment_image(apt.name, new_url):
                        print(f"✅ Updated {apt.name} with image: {new_url}")
                        updated_count += 1
                    else:
                        print(f"❌ Failed to update {apt.name}")
                    found = True
                    break
            if not found:
                print(f"⚠️ Apartment '{apt_name}' not found in database.")
        print(f"\n--- Bulk Update Complete. {updated_count} apartments updated. ---")


def main():
    updater = ManualImageInput(engine)
    
    while True:
        print("\nSelect an option:")
        print("1. List all apartments and their current image status")
        print("2. Update a specific apartment by name (interactive)")
        print("3. Interactive update for all apartments")
        print("4. Bulk update (paste multiple name:url pairs)")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            updater.list_all_apartments()
        elif choice == '2':
            apt_name = input("Enter the name of the apartment to update: ").strip()
            apartments = updater.get_all_apartments()
            found_apt = None
            for apt in apartments:
                if apt_name.lower() in apt.name.lower():
                    found_apt = apt
                    break
            
            if found_apt:
                print(f"\nApartment: {found_apt.name}")
                print(f"Current image: {found_apt.image_url or 'No image'}")
                new_url = input("Enter new image URL: ").strip()
                if new_url:
                    if updater.update_apartment_image(found_apt.name, new_url):
                        print(f"✅ Updated {found_apt.name} with image: {new_url}")
                    else:
                        print(f"❌ Failed to update {found_apt.name}")
                else:
                    print("No URL provided. Skipping update.")
            else:
                print(f"Apartment '{apt_name}' not found.")
        elif choice == '3':
            updater.interactive_update()
        elif choice == '4':
            updater.bulk_update()
        elif choice == '5':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
