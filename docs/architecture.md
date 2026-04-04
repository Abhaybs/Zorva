# Zorva GigShield — Architecture

## System Overview

Zorva operates as a 5-layer stack, each designed for independence and horizontal scaling.

## Layer 1: Android App (Kotlin)

**Purpose:** Everything the gig worker touches directly.

| Module | Function | Key Tech |
|--------|----------|----------|
| Dashboard | GigScore gauge + income charts | ViewModel + LiveData |
| SOS & GPS | One-tap emergency + live tracking | FusedLocationProvider |
| OCR Scanner | Screenshot → earnings extraction | ML Kit Text Recognition |
| SMS Reader | Auto-capture payment SMS | BroadcastReceiver |
| Legal Shield | Appeal generator + rights guide | Template engine |

**Why Kotlin native?** Background services (SOS GPS, SMS monitoring) work far more reliably in native Android than cross-platform frameworks.

## Layer 2: FastAPI Backend

**Purpose:** 5 dedicated APIs handling all business logic.

| API | Endpoint Prefix | Key Function |
|-----|----------------|--------------|
| Income | `/api/v1/income` | Cross-platform earnings aggregation |
| GigScore | `/api/v1/gigscore` | Trigger ML model, return score |
| Insurance | `/api/v1/insurance` | Micro-insurance plans + claims |
| SOS | `/api/v1/sos` | GPS broadcast + FCM push alerts |
| Schemes | `/api/v1/schemes` | Government welfare eligibility match |

**Auth:** Firebase Auth (mobile) → JWT (internal API calls).
**Async advantage:** FastAPI's async-first design handles real-time SOS load well.

## Layer 3: AI/ML Engine

| Model | Algorithm | Score Range | Primary Inputs |
|-------|-----------|-------------|----------------|
| GigScore | Random Forest Regressor | 0–900 | Income CV, trips, rating, patterns, diversity |
| Fatigue | Gradient Boosting Classifier | Low/Med/High | Hours, distance, breaks, late-night work |
| Earnings | Gradient Boosting Regressor | ₹/hour | Zone coords, time, demand, active workers |
| OCR+NLP | Tesseract + Regex | Structured data | Screenshot images, SMS text |

## Layer 4: Data Layer

| Store | Purpose | Key Features |
|-------|---------|--------------|
| PostgreSQL + PostGIS | Worker profiles, income history, policies | Geospatial zone queries |
| Firebase RTDB | Live SOS events, real-time tracking | WebSocket push, FCM |
| Razorpay | Insurance premiums, cash advance | Payment gateway |
| Account Aggregator | Bank transaction linking | RBI-regulated consent |

## Layer 5: Data Inputs (Consent-Based)

All data collection is consent-based and platform-independent:

1. **SMS Parsing** — Auto-capture Swiggy/Ola/Zomato payment alerts
2. **Screenshot OCR** — Upload earnings dashboard photos
3. **Bank AA Link** — RBI Account Aggregator for bank transactions
4. **Manual/Voice Log** — Regional language offline fallback

This design answers the key judge question: **"How do you get data without platform APIs?"**
