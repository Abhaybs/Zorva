"""Income Aggregator service — business logic for cross-platform income."""

from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.income import IncomeRecord


class IncomeAggregator:
    """Aggregates income across platforms with analytics."""

    async def daily_breakdown(
        self, db: AsyncSession, worker_id: Any, days: int = 30
    ) -> list[dict]:
        """Get daily earnings breakdown for the given period."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        result = await db.execute(
            select(
                func.date(IncomeRecord.earned_at).label("date"),
                func.sum(IncomeRecord.amount).label("total"),
                func.count(IncomeRecord.id).label("records"),
            )
            .where(IncomeRecord.worker_id == worker_id)
            .where(IncomeRecord.earned_at >= cutoff)
            .group_by(func.date(IncomeRecord.earned_at))
            .order_by(func.date(IncomeRecord.earned_at))
        )

        return [
            {"date": str(row.date), "total": float(row.total), "records": row.records}
            for row in result.all()
        ]

    async def platform_breakdown(
        self, db: AsyncSession, worker_id: Any, days: int = 30
    ) -> list[dict]:
        """Get earnings breakdown by platform."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        result = await db.execute(
            select(
                IncomeRecord.platform,
                func.sum(IncomeRecord.amount).label("total"),
                func.count(IncomeRecord.id).label("records"),
            )
            .where(IncomeRecord.worker_id == worker_id)
            .where(IncomeRecord.earned_at >= cutoff)
            .group_by(IncomeRecord.platform)
            .order_by(func.sum(IncomeRecord.amount).desc())
        )

        return [
            {
                "platform": row.platform.value,
                "total": float(row.total),
                "records": row.records,
            }
            for row in result.all()
        ]
