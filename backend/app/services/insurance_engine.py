"""Insurance Engine service — premium calculation and claims processing."""

from __future__ import annotations
from typing import Any


class InsuranceEngine:
    """
    Calculates dynamic premiums based on GigScore and worker profile.

    In production, this would integrate with insurance provider APIs
    and use actuarial models for premium calculation.
    """

    BASE_PREMIUMS = {
        "accident": 5.0,
        "health": 8.0,
        "vehicle": 7.0,
        "income_protection": 10.0,
    }

    def calculate_premium(
        self, insurance_type: str, gigscore: float, worker: Any
    ) -> dict:
        """
        Calculate personalised daily premium based on GigScore.

        Higher GigScore = lower premium (more reliable worker = less risk).
        """
        base = self.BASE_PREMIUMS.get(insurance_type, 10.0)

        # Score-based discount (0–900 scale)
        if gigscore >= 750:
            discount = 0.25  # 25% discount
        elif gigscore >= 600:
            discount = 0.15
        elif gigscore >= 450:
            discount = 0.05
        else:
            discount = 0.0

        final_premium = round(base * (1 - discount), 2)

        return {
            "insurance_type": insurance_type,
            "base_premium": base,
            "gigscore_discount": f"{discount * 100:.0f}%",
            "final_daily_premium": final_premium,
            "monthly_estimate": round(final_premium * 30, 2),
        }

    def validate_claim(self, policy: Any, claim_amount: float) -> dict:
        """Validate a claim against policy terms."""
        issues = []

        if claim_amount > policy.coverage_amount:
            issues.append(
                f"Claim ₹{claim_amount} exceeds coverage ₹{policy.coverage_amount}"
            )

        if policy.status != "active":
            issues.append(f"Policy is {policy.status}, not active")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }
