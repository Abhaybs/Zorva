# Zorva — GigShield

> AI-powered financial identity & protection for India's gig workers

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Layer 1 — Android App (Kotlin)                     │
│  Dashboard │ SOS+GPS │ OCR Scanner │ SMS │ Legal    │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS / JWT
┌──────────────────────▼──────────────────────────────┐
│  Layer 2 — FastAPI Backend (Python)                 │
│  Income API │ GigScore │ Insurance │ SOS │ Schemes  │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  Layer 3 — AI/ML Engine                             │
│  GigScore RF │ Fatigue │ Earnings AI │ OCR+NLP      │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  Layer 4 — Data Layer                               │
│  PostgreSQL+PostGIS │ Firebase RT │ Razorpay │ AA   │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env   # Edit database URL
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for Swagger UI.

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

### Android App

1. Open `android/` in **Android Studio**
2. Sync Gradle
3. Run on emulator or device (API 26+)
4. Backend URL defaults to `10.0.2.2:8000` (emulator → host)

## Project Structure

```
Gigshield/
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── api/          # 5 route modules
│   │   ├── auth/         # Firebase + JWT
│   │   ├── models/       # SQLAlchemy ORM
│   │   ├── schemas/      # Pydantic validation
│   │   ├── services/     # Business logic
│   │   └── db/           # Database layer
│   └── requirements.txt
├── ml_engine/            # AI/ML pipeline
│   ├── models/
│   │   ├── gigscore/     # Random Forest (0-900 score)
│   │   ├── fatigue/      # Gradient Boosting detector
│   │   ├── earnings/     # Zone optimizer
│   │   └── ocr_nlp/      # OCR + SMS parser
│   └── data/synthetic/   # Training data generator
├── android/              # Kotlin MVVM app
│   └── app/src/main/
│       ├── java/com/zorva/gigshield/
│       │   ├── ui/       # 5 screens
│       │   ├── data/     # Retrofit + models
│       │   └── services/ # GPS + SMS background
│       └── res/          # Layouts + themes
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
| GET | `/api/v1/insurance/plans` | Available micro-insurance |
| POST | `/api/v1/insurance/subscribe` | Subscribe to plan |
| POST | `/api/v1/insurance/claim` | File claim |
| POST | `/api/v1/sos/trigger` | Emergency SOS |
| GET | `/api/v1/sos/status/{id}` | SOS event status |
| PUT | `/api/v1/sos/resolve/{id}` | Resolve SOS |
| GET | `/api/v1/schemes/eligible` | Matched govt schemes |
| GET | `/api/v1/schemes/all` | All welfare schemes |

## ML Models

| Model | Algorithm | Input | Output |
|-------|-----------|-------|--------|
| GigScore | Random Forest | 16 features from income history | Score 0-900 |
| Fatigue | Gradient Boosting | Hours, distance, breaks, patterns | Risk level (low/med/high) |
| Earnings | Gradient Boosting | Zone, time, demand, workers | ₹/hour prediction |
| OCR | Tesseract + Regex | Screenshot image | Structured earnings data |
| SMS | Regex + NLP | Payment SMS text | Amount + platform + ref |

## Tech Stack

- **Android**: Kotlin, MVVM, Retrofit, Firebase, ML Kit, Material 3
- **Backend**: FastAPI, SQLAlchemy, Async PostgreSQL, Firebase Auth
- **ML**: Scikit-learn, Tesseract OCR, Pandas, NumPy
- **Data**: PostgreSQL + PostGIS, Firebase Realtime DB

## License

Proprietary — Zorva Technologies
