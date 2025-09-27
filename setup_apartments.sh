#!/bin/bash

# Setup script for apartment data integration
echo "Setting up apartment data for Bedathon..."

# Navigate to backend directory
cd backend

# Install new dependencies
echo "Installing new dependencies..."
pip install pandas==2.1.4 openpyxl==3.1.2

# Initialize database
echo "Initializing database..."
python init_db.py

# Import apartment data
echo "Importing apartment data from Google Sheets..."
python import_apartments.py

echo "Apartment data setup complete!"
echo ""
echo "To start the backend server:"
echo "cd backend && python app.py"
echo ""
echo "To start the frontend server:"
echo "cd frontend && npm run dev"
echo ""
echo "The apartment data is now available at:"
echo "- GET /apartments - List all apartments with filtering"
echo "- GET /apartments/{id} - Get specific apartment"
echo "- POST /apartments/import - Re-import data from Google Sheets"
