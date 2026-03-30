from datetime import datetime, timedelta

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import SoftDeleteModel

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


class Treatment(SoftDeleteModel):
    __tablename__ = "treatment"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    date_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    receipt: Mapped[str] = mapped_column(String(1024), nullable=False)

    __table_args__ = (Index("ix_treatment_user_id", "user_id"),)

    @property
    def status(self) -> str:
        now = datetime.now(KYIV_TZ)
        end_date = self.date_start + timedelta(days=self.days)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=KYIV_TZ)
        return "active" if end_date > now else "completed"
