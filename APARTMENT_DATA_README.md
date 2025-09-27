# Apartment Data Integration

This document describes the apartment data integration that pulls data from the Virginia Tech Parents Facebook Group spreadsheet and integrates it into the Bedathon application.

## Data Source

The apartment data comes from the [2025-2026 Off Campus Housing Information](https://docs.google.com/spreadsheets/d/1KugYXAnZXYYM-YJ9x-u-OyqKuPf60vgSsO3a5l0VVlA/edit?gid=0#gid=0) spreadsheet maintained by the Virginia Tech Parents Facebook Group.

## Features

### Backend Integration

1. **Database Models** (`backend/models.py`)
   - `ApartmentComplex` - Main apartment data model
   - `ApartmentComplexCreate` - For creating new apartments
   - `ApartmentComplexRead` - For API responses

2. **Data Import** (`backend/import_apartments.py`)
   - Parses apartment data from the Google Sheets
   - Handles data cleaning and validation
   - Imports 20+ apartment complexes with detailed information

3. **API Endpoints** (`backend/app.py`)
   - `GET /apartments` - List apartments with filtering
   - `GET /apartments/{id}` - Get specific apartment
   - `POST /apartments` - Create new apartment
   - `PUT /apartments/{id}` - Update apartment
   - `DELETE /apartments/{id}` - Delete apartment
   - `POST /apartments/import` - Re-import data from Google Sheets

### Frontend Integration

1. **Service Layer** (`frontend/lib/apartmentService.ts`)
   - `ApartmentService` class for API communication
   - `formatApartmentForDisplay` helper function
   - TypeScript interfaces for type safety

2. **React Hooks** (`frontend/lib/useApartments.ts`)
   - `useApartments` hook for fetching apartment lists
   - `useApartment` hook for fetching individual apartments
   - Loading states and error handling

3. **UI Updates** (`frontend/app/page.tsx`)
   - Real apartment data display
   - Loading states and error handling
   - Enhanced apartment details dialog

## Data Fields

Each apartment complex includes:

- **Basic Info**: Name, address, phone number
- **Pricing**: Studio through 5-bedroom costs
- **Lease Details**: Term length, type (Individual/Joint)
- **Amenities**: Pets, parking, furniture, utilities, laundry
- **Location**: Distance to campus, bus stop availability
- **Fees**: Application fee, security deposit, additional fees
- **Notes**: Special information and updates

## Setup Instructions

1. **Install Dependencies**
   ```bash
   cd backend
   pip install pandas==2.1.4 openpyxl==3.1.2
   ```

2. **Initialize Database**
   ```bash
   python init_db.py
   ```

3. **Import Apartment Data**
   ```bash
   python import_apartments.py
   ```

4. **Start Backend Server**
   ```bash
   python app.py
   ```

5. **Start Frontend Server**
   ```bash
   cd frontend
   npm run dev
   ```

## API Usage Examples

### Get All Apartments
```bash
curl "http://localhost:8000/apartments"
```

### Filter Apartments
```bash
# Search by name
curl "http://localhost:8000/apartments?search=Alight"

# Filter by distance
curl "http://localhost:8000/apartments?max_distance=2.0"

# Filter by pets allowed
curl "http://localhost:8000/apartments?pets_allowed=true"

# Combine filters
curl "http://localhost:8000/apartments?pets_allowed=true&parking_included=true&max_distance=1.5"
```

### Get Specific Apartment
```bash
curl "http://localhost:8000/apartments/{apartment_id}"
```

### Re-import Data
```bash
curl -X POST "http://localhost:8000/apartments/import"
```

## Data Updates

The apartment data can be updated by:

1. **Manual Re-import**: Use the `/apartments/import` endpoint
2. **Update Script**: Run `python import_apartments.py` directly
3. **API Updates**: Use the CRUD endpoints to modify individual apartments

## Notes

- The data is sourced from the Virginia Tech Parents Facebook Group and is subject to their terms
- Pricing information may not be current - contact properties directly for up-to-date rates
- Some fields may be incomplete or marked as "Contact for details"
- The integration handles data cleaning and validation automatically

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure DATABASE_URL is set in your environment
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **Import Errors**: Check that the import script can access the data
4. **Frontend Errors**: Ensure the backend is running on the correct port

### Support

For issues with the apartment data integration, check:
- Backend logs for API errors
- Frontend console for JavaScript errors
- Database connection and table creation
- Network connectivity between frontend and backend
