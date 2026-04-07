from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import BaseModel


class NotificationDismissalModel(BaseModel):
    __tablename__ = "notification_dismissal"
    __table_args__ = (
        UniqueConstraint("user_id", "entity_type", "entity_id", "reminder_type", name="uq_dismissal"),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)  # visit, treatment, vaccination
    entity_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reminder_type: Mapped[str] = mapped_column(String(20), nullable=False)  # day_before, hour_before
