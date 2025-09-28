# HokieNest 🏠

**Roommates and Housing Matching for Virginia Tech**

HokieNest helps VT students find compatible roommates and discover apartments that fit their preferences (budget, bedrooms, distance, amenities). It combines a modern **Next.js frontend** with a **FastAPI backend**, **Supabase integration**, and a local **SQLite fallback** for development.

---

## ✨ Key Features

- 🔗 Roommate matching based on lifestyle preferences, budget, year, and major  
- 🏘 Apartment matching by distance to VT, bedrooms, budget fit, and amenity overlap  
- 🎨 Clean, responsive UI built with Shadcn UI + Tailwind CSS  
- 🔑 OAuth sign-in with Google (via Supabase Auth)  
- 🗄 Supabase profiles with optional local SQLite for development  
- 📞 Voice call integration (optional) to “get the latest info” from an apartment  

---

## 🏗 Architecture

**Frontend (`frontend/`)**
- Framework: Next.js (App Router), React, TypeScript  
- Styling: Tailwind CSS + Shadcn UI  
- Auth: Supabase Auth  

**Backend (`backend/`)**
- Framework: FastAPI (Uvicorn)  
- Data: Supabase (production) or SQLite (development fallback)  
- Matching: Python algorithms for roommates and apartments  

**Data Sources**
- Apartment data: imported from VT JSON sources or Supabase DB  
- Profiles: stored in Supabase `profiles` table via backend APIs  

---

## 🧮 Matching Algorithms

**Roommate Matching (default weights)**
- Lifestyle vector (cleanliness, noise, study, social, sleep): 50%  
- Budget proximity: 25%  
- Year match: 10%  
- Major similarity: 15%  

Formula:  
`score = 0.50*lifestyle + 0.25*budget + 0.10*year + 0.15*major`

**Apartment Matching (default weights)**
- Price fit: 35% (best within ±10% of budget)  
- Distance to VT: 30% (best near 0.5 miles)  
- Amenity overlap: 20% (Laundry, Parking, WiFi bonuses)  
- Study-friendliness: 10% (WiFi + no pool if study-focused)  
- Parking: 5%  

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+  
- Python 3.10+  
- Supabase project (optional for local dev; required for full profiles)  
- macOS/Linux recommended  

### Environment Variables
Create:  
- `frontend/.env.local`  
- `backend/.env`  

💡 For local dev, omit `DATABASE_URL` to use `sqlite:///./bedathon.db`.

### Install and Run

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## 🌱 Seeding Apartment Data (local dev)

```bash
cd backend
python import_apartments_to_db.py
```

## 🔑 Sign-in and Profiles

1. Click "Sign in with Google" on the landing page
2. Complete onboarding form (budget, bedrooms, preferences)
3. Backend creates/updates Supabase profile
4. Access Roommate Matches and Apartment Matches tabs

## 🔌 API Overview (Backend)

**Base URL:** `http://localhost:8000`

### Core Endpoints
- `GET /health` → Health check
- `POST /profiles` → Create/update profile
- `GET /profiles/me` → Fetch current profile
- `PUT /profiles/me` → Update profile

### Matching Endpoints
- `POST /matching/roommate-preferences` → Save preferences
- `POST /matching/roommate-matches` → Get roommate matches
- `POST /matching/apartment-matches-for-preferences` → Get apartment matches
- `GET /matching/apartment-matches/{profile_id}?limit=100` → Matches for profile
- `GET /matching/apartments` → All apartments

> **Note:** Voice call endpoint exists in codebase but may be disabled.

## 🎨 Frontend Walkthrough

- **Onboarding** → Form for budget, bedrooms, lifestyle preferences
- **Roommate Matches** → Grid with compatibility badges
- **Apartment Matches** → Price, distance, amenity badges + "why it matches" reasons

## 🛠 Development Tips

### Port Management
- **Next.js** auto-increments ports (3000 → 3001…)
- Ensure `NEXT_PUBLIC_BACKEND_URL` matches backend (default: 8000)

### Database Options
- **SQLite:** Omit `DATABASE_URL` for local SQLite
- **Reset:** Delete/recreate `bedathon.db` if errors occur
- **Supabase Postgres:** Use actual DB credentials, not service role key

### Authentication
- If `/profiles` returns 401, re-login and check Bearer token is sent

## 📜 Scripts & Utilities

| Script | Purpose |
|--------|---------|
| `backend/import_apartments_to_db.py` | Import JSON apartments |
| `backend/comprehensive_data_scraper.py` | Scrape VT housing data |
| `backend/update_apartments_from_vt_sheet.py` | Sync from sheet |
| `backend/test_matching_api.py` | Sample API calls |

## 🗺 Roadmap

- [ ] **Save/Like** apartments and roommate profiles
- [ ] **Group-based** housing recommendations
- [ ] **Map view** with filters by distance/amenities
- [ ] **Availability and contact** integration per apartment

## 📝 License

MIT (or your preferred license)

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Shadcn UI](https://ui.shadcn.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/) / [SQLAlchemy](https://www.sqlalchemy.org/)
- [Supabase](https://supabase.com/)
- VT community datasets and housing resources

---

<div align="center">
  <p>Built with ❤️ for the Virginia Tech community</p>
  <p><strong>Go Hokies! 🦃</strong></p>
</div>
