from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import BaseModel


class PushSentLogModel(BaseModel):
    __tablename__ = "push_sent_log"
    __table_args__ = (
        UniqueConstraint("user_id", "entity_type", "entity_id", "reminder_type", name="uq_push_sent"),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reminder_type: Mapped[str] = mapped_column(String(20), nullable=False)
