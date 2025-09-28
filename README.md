# Bed-A-Thon 🏠

**Roommates and Housing Matching for Virginia Tech**

Bed-A-Thon helps VT students find compatible roommates and discover apartments that fit their preferences (budget, bedrooms, distance, amenities). It combines a modern **Next.js frontend** with a **FastAPI backend**, **Supabase integration**, and a local **SQLite fallback** for development.

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

## 🤖 AI Agent - Apartment Information Service

HokieNest includes an intelligent AI agent that streamlines the apartment hunting process:

- **Automated Calling** → Agent calls apartments that roommates have selected
- **Information Gathering** → Collects current pricing, bedroom availability, amenities, and lease terms
- **Summary Generation** → Creates comprehensive email summaries with all collected details
- **Real-time Updates** → Ensures apartment information is current and accurate

The AI agent eliminates the need for students to make multiple phone calls, saving time and providing standardized information across all potential housing options.

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

## 📸 Screenshots

> Add screenshots to `frontend/public/` and embed them here:

```markdown
![Landing Page](frontend/public/screenshots/landing.png)
![Onboarding](frontend/public/screenshots/onboarding.png)
![Roommate Matches](frontend/public/screenshots/roommate-matches.png)
![Apartment Matches](frontend/public/screenshots/apartment-matches.png)
```

## 🤝 Contributing

1. **Fork** this repo
2. **Create** a feature branch (`git checkout -b feature/my-feature`)
3. **Run** linters/tests before pushing
4. **Open** a PR with description + screenshots if UI changes

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
