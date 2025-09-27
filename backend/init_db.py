#!/usr/bin/env python3
"""
Database initialization script for Bedathon.
Creates all necessary tables and imports initial data.
"""

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
from models import Profile, ApartmentComplex

load_dotenv()

def init_database():
    """Initialize the database with all tables."""
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bedathon.db")
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
