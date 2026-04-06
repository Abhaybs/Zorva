# Zorva — GigShield

> AI-powered financial identity & protection for India's gig workers

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Layer 1 — Android App (Kotlin)                     │
│  Dashboard │ GigScore │ Earn More │ SOS │ OCR │ Legal│
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS / Supabase JWT
┌──────────────────────▼──────────────────────────────┐
│  Layer 2 — FastAPI Backend (Python)                 │
│  Income API │ GigScore │ Earnings Optimizer │ SOS   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  Layer 3 — AI/ML Engine                             │
│  GigScore RF │ Fatigue │ Earnings AI │ OCR+NLP      │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  Layer 4 — Data Layer                               │
│  Supabase PostgreSQL │ Firebase RT │ PostGIS         │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env   # Edit Supabase URL, keys, DB URL
# Run from the backend/ directory:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open **http://localhost:8000/docs** for Swagger UI.

> **Note**: Always start uvicorn from inside the `backend/` directory using `app.main:app` (not `backend.app.main:app`).

### Android (Local Dev with Physical Device)

```bash
# Forward device traffic to local backend
adb reverse tcp:8000 tcp:8000
```

1. Open `android/` in **Android Studio**
2. Sync Gradle
3. Run on device (API 26+)
4. Backend URL is `http://127.0.0.1:8000` (via ADB reverse)

### ML Engine

```bash
cd ml_engine
pip install -r requirements.txt

# Generate synthetic training data
python data/synthetic/generate_data.py

# Train models
python models/gigscore/train.py
python models/fatigue/train.py
python models/earnings/train.py

# Test predictions
python models/gigscore/predict.py
python models/fatigue/predict.py
python models/earnings/predict.py
```

## Project Structure

```
Gigshield/
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── api/          # Route modules (income, gigscore, earnings, sos, schemes, insurance)
│   │   ├── auth/         # Supabase JWT + Firebase fallback
│   │   ├── models/       # SQLAlchemy ORM
│   │   ├── schemas/      # Pydantic validation
│   │   ├── services/     # Business logic + ML integration
│   │   └── db/           # Async PostgreSQL (asyncpg/NullPool)
│   └── requirements.txt
├── ml_engine/            # AI/ML pipeline
│   ├── models/
│   │   ├── gigscore/     # Random Forest (0-900 score)
│   │   ├── fatigue/      # Gradient Boosting detector
│   │   ├── earnings/     # Zone optimizer (location-aware)
│   │   └── ocr_nlp/      # OCR + SMS parser
│   └── data/synthetic/   # Training data generator
├── android/              # Kotlin MVVM app
│   └── app/src/main/
│       ├── java/com/zorva/gigshield/
│       │   ├── ui/       # 6 screens: Dashboard, GigScore, Earn More, SOS, OCR, Legal
│       │   ├── data/     # Retrofit + models + Supabase auth
│       │   └── services/ # GPS + SMS background services
│       └── res/          # Layouts + Material 3 dark theme
└── docs/                 # Documentation
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/income/record` | Add income entry |
| GET | `/api/v1/income/summary` | Aggregated earnings |
| GET | `/api/v1/income/history` | Detailed income list |
| POST | `/api/v1/gigscore/calculate` | Trigger ML scoring |
| GET | `/api/v1/gigscore/current` | Latest GigScore |
| GET | `/api/v1/gigscore/history` | Score trend |
| GET | `/api/v1/earnings/zones` | Top zones by ₹/hr (supports `?lat=&lng=`) |
| GET | `/api/v1/earnings/best-hours` | Best hours for a zone |
| GET | `/api/v1/earnings/zones/list` | All available zone names |
| GET | `/api/v1/insurance/plans` | Available micro-insurance |
| POST | `/api/v1/insurance/subscribe` | Subscribe to plan |
| POST | `/api/v1/insurance/claim` | File claim |
| POST | `/api/v1/sos/trigger` | Emergency SOS (auth-resolved worker) |
| GET | `/api/v1/sos/status/{id}` | SOS event status |
| PUT | `/api/v1/sos/resolve/{id}` | Resolve SOS |
| GET | `/api/v1/schemes/eligible` | Matched govt schemes |
| GET | `/api/v1/schemes/all` | All welfare schemes |

## ML Models

| Model | Algorithm | Input | Output |
|-------|-----------|-------|--------|
| GigScore | Random Forest | 16 features from income history | Score 0-900 |
| Fatigue | Gradient Boosting | Hours, distance, breaks, patterns | Risk level (low/med/high) |
| Earnings | Heuristic + Haversine filter | Zone, time, demand, GPS coords | ₹/hour prediction, filtered to 50km radius |
| OCR | Tesseract + Regex | Screenshot image | Structured earnings data |
| SMS | Regex + NLP | Payment SMS text | Amount + platform + ref |

## Android Screens

| Screen | Nav Tab | Description |
|--------|---------|-------------|
| Dashboard | Home | Platform earnings, best zone banner, quick tiles |
| GigScore | Score | Score circle (0-900), 5-factor breakdown, recalculate |
| Earn More | (via Dashboard tile / Best Zone card) | Top zones by ₹/hr, best hours per zone |
| Income OCR | Income | Scan earnings screenshots |
| Legal Shield | Shield | Government schemes & rights |
| SOS | More | Hold-to-trigger emergency, nearby workers |

## Auth

All endpoints require a **Supabase Bearer token** in the `Authorization` header. Worker identity is resolved server-side from the token — no `worker_id` in request bodies.

## Tech Stack

- **Android**: Kotlin, MVVM, ViewBinding, Retrofit, Supabase Auth, Material 3, FusedLocationProvider
- **Backend**: FastAPI, SQLAlchemy (asyncio), asyncpg, NullPool (PgBouncer-compatible), Supabase JWT
- **ML**: Scikit-learn, Tesseract OCR, Pandas, NumPy
- **Data**: Supabase PostgreSQL, Firebase Realtime DB
