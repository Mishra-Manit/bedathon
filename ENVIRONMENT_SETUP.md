# Environment Setup for Supabase Integration

## Frontend Environment Variables (.env.local)

Create a file called `.env.local` in the `frontend/` directory with the following content:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Backend Environment Variables (.env)

Create a file called `.env` in the `backend/` directory with the following content:

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Database Configuration
DATABASE_URL=sqlite:///./bedathon.db

# Anthropic API (for Claude agent)
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## How to Get Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** > **API**
3. Copy the following values:
   - **Project URL** → Use for `SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public** key → Use for `SUPABASE_ANON_KEY` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **service_role** key → Use for `SUPABASE_SERVICE_ROLE_KEY`

## Quick Setup Commands

Run these commands in your terminal:

```bash
# Navigate to frontend directory
cd frontend

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
EOF

# Navigate to backend directory
cd ../backend

# Create .env file
cat > .env << EOF
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
DATABASE_URL=sqlite:///./bedathon.db
ANTHROPIC_API_KEY=your_anthropic_api_key
EOF
```

## After Setting Up Environment Variables

1. **Restart the frontend server**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Restart the backend server**:
   ```bash
   cd backend
   python app.py
   ```

3. **Test the Supabase connection** by visiting:
   - Frontend: http://localhost:3002
   - Roommate Matching: http://localhost:3002/roommate-matching
   - API: http://localhost:8000/matching/data-summary

## Current Status

✅ **Backend**: Already configured to use Supabase
✅ **Frontend**: Already configured to use Supabase  
✅ **Database**: Using your existing Supabase database
✅ **Models**: Integrated with your Profile and ApartmentComplex tables

## What This Enables

- **Real-time data**: All roommate profiles and apartment data stored in Supabase
- **Authentication**: User login/logout through Supabase Auth
- **Real apartments**: 21 real apartments from your database
- **Persistent storage**: All data saved and accessible across sessions
- **Scalable**: Ready for production deployment

Replace the placeholder values with your actual Supabase credentials and you'll have a fully integrated system!
