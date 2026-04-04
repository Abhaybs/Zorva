"""Government Scheme Matcher — matches worker profile to welfare schemes."""

from __future__ import annotations
from typing import Any


# ── Known Indian welfare schemes relevant to gig workers ──────
SCHEMES_DATABASE = [
    {
        "id": "esic",
        "name": "ESIC (Employee State Insurance Corporation)",
        "description": "Social security for gig/platform workers — medical, disability, maternity benefits.",
        "eligibility": "Platform workers earning less than ₹21,000/month",
        "benefit": "Medical treatment, cash during sickness, maternity, disability pension",
        "url": "https://www.esic.gov.in",
        "category": "social_security",
    },
    {
        "id": "pmsby",
        "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
        "description": "Accidental death & disability insurance at ₹20/year premium.",
        "eligibility": "All Indian citizens aged 18-70 with a bank account",
        "benefit": "₹2 lakh accidental death, ₹1 lakh partial disability",
        "url": "https://jansuraksha.gov.in",
        "category": "insurance",
    },
    {
        "id": "pmjjby",
        "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
        "description": "Life insurance at ₹436/year premium.",
        "eligibility": "All Indian citizens aged 18-55 with a bank account",
        "benefit": "₹2 lakh life insurance cover",
        "url": "https://jansuraksha.gov.in",
        "category": "insurance",
    },
    {
        "id": "epfo_gig",
        "name": "EPFO for Gig Workers",
        "description": "Provident fund enrollment for platform/gig workers under Code on Social Security 2020.",
        "eligibility": "Gig and platform workers as defined in SS Code 2020",
        "benefit": "Retirement savings, pension, life insurance",
        "url": "https://www.epfindia.gov.in",
        "category": "retirement",
    },
    {
        "id": "ayushman_bharat",
        "name": "Ayushman Bharat (PM-JAY)",
        "description": "Health insurance cover of ₹5 lakh per family per year.",
        "eligibility": "Families with income below poverty threshold",
        "benefit": "Free hospitalization up to ₹5 lakh/year at empanelled hospitals",
        "url": "https://pmjay.gov.in",
        "category": "health",
    },
    {
        "id": "mudra",
        "name": "Pradhan Mantri Mudra Yojana (PMMY)",
        "description": "Micro-loans up to ₹10 lakh for small businesses and self-employed.",
        "eligibility": "Non-corporate, non-farm small/micro enterprises",
        "benefit": "Collateral-free loans: Shishu (₹50K), Kishore (₹5L), Tarun (₹10L)",
        "url": "https://www.mudra.org.in",
        "category": "finance",
    },
    {
        "id": "eShram",
        "name": "eShram Portal",
        "description": "National registration portal for unorganized workers including gig workers.",
        "eligibility": "All unorganized/gig workers aged 16-59",
        "benefit": "Unique UAN, accidental insurance of ₹2 lakh, access to govt schemes",
        "url": "https://eshram.gov.in",
        "category": "registration",
    },
    {
        "id": "stand_up_india",
        "name": "Stand Up India",
        "description": "Loans from ₹10 lakh to ₹1 crore for SC/ST and women entrepreneurs.",
        "eligibility": "SC/ST and women entrepreneurs for greenfield enterprises",
        "benefit": "Bank loan between ₹10L and ₹1Cr for setting up enterprise",
        "url": "https://www.standupmitra.in",
        "category": "finance",
    },
]


class SchemeMatcher:
    """Matches worker profiles to eligible government welfare schemes."""

    def get_all_schemes(self) -> list[dict]:
        """Return all known schemes."""
        return SCHEMES_DATABASE

    def match_schemes(self, worker: Any) -> list[dict]:
        """
        Match a worker's profile to eligible schemes.

        In production, this would use worker's income data, age, city,
        caste category, and other factors for precise matching.
        Currently returns universally-applicable schemes plus
        income-based recommendations.
        """
        eligible = []

        for scheme in SCHEMES_DATABASE:
            # Universal eligibility schemes
            if scheme["id"] in ("pmsby", "pmjjby", "eShram", "mudra"):
                eligible.append({
                    **scheme,
                    "match_reason": "Universally available to gig workers",
                    "match_confidence": 0.95,
                })
            elif scheme["id"] == "esic":
                eligible.append({
                    **scheme,
                    "match_reason": "Available for platform workers under Social Security Code 2020",
                    "match_confidence": 0.85,
                })
            elif scheme["id"] == "epfo_gig":
                eligible.append({
                    **scheme,
                    "match_reason": "EPFO extended to gig/platform workers",
                    "match_confidence": 0.80,
                })
            elif scheme["id"] == "ayushman_bharat":
                eligible.append({
                    **scheme,
                    "match_reason": "Income-based eligibility — verify income threshold",
                    "match_confidence": 0.60,
                })

        return eligible
