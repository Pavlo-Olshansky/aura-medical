from __future__ import annotations

import math
from abc import abstractmethod
from datetime import date, datetime, time
from typing import Any, Generic, Optional, Sequence, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.base import Base

TModel = TypeVar("TModel", bound=Base)
TEntity = TypeVar("TEntity")


def normalize_date_to_datetime(d: date | datetime, *, end: bool = False) -> datetime:
    """Convert a plain ``date`` to ``datetime`` using min/max time."""
    if isinstance(d, datetime):
        return d
    t = time.max if end else time.min
    return datetime.combine(d, t)


class BaseQueryRepository(Generic[TModel, TEntity]):
    """Shared query utilities for SQLAlchemy async repositories."""

    model_class: type[TModel]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Query building helpers
    # ------------------------------------------------------------------

    def _base_query(self) -> Select[tuple[TModel]]:
        stmt = select(self.model_class)
        if hasattr(self.model_class, "deleted_at"):
            stmt = stmt.where(self.model_class.deleted_at.is_(None))  # type: ignore[attr-defined]
        return stmt

    def _base_count(self) -> Select[tuple[int]]:
        stmt = select(func.count()).select_from(self.model_class)
        if hasattr(self.model_class, "deleted_at"):
            stmt = stmt.where(self.model_class.deleted_at.is_(None))  # type: ignore[attr-defined]
        return stmt

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_date_filter(
        query: Select,
        count_query: Select,
        column: Any,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> tuple[Select, Select]:
        if date_from:
            dt = normalize_date_to_datetime(date_from, end=False)
            query = query.where(column >= dt)
            count_query = count_query.where(column >= dt)
        if date_to:
            dt = normalize_date_to_datetime(date_to, end=True)
            query = query.where(column <= dt)
            count_query = count_query.where(column <= dt)
        return query, count_query

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def _apply_sort(
        self,
        query: Select,
        sort: str,
        sort_map: Optional[dict[str, Any]] = None,
    ) -> Select:
        mc = self.model_class
        if sort_map is None:
            sort_map = {
                "date": mc.date,  # type: ignore[attr-defined]
                "-date": mc.date.desc(),  # type: ignore[attr-defined]
                "created": mc.created,  # type: ignore[attr-defined]
                "-created": mc.created.desc(),  # type: ignore[attr-defined]
                "id": mc.id,  # type: ignore[attr-defined]
                "-id": mc.id.desc(),  # type: ignore[attr-defined]
            }
        order = sort_map.get(sort)
        if order is None:
            # Fallback: descending by date if available, otherwise by id
            order = sort_map.get("-date", mc.id.desc())  # type: ignore[attr-defined]
        return query.order_by(order)

    # ------------------------------------------------------------------
    # Pagination
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_pagination(query: Select, page: int, size: int) -> Select:
        offset = (page - 1) * size
        return query.offset(offset).limit(size)

    @staticmethod
    def _paginated_result(
        items: Sequence[TEntity],
        total: int,
        page: int,
        size: int,
    ) -> dict[str, Any]:
        return {
            "items": list(items),
            "total": total,
            "page": page,
            "size": size,
            "pages": math.ceil(total / size) if size else 0,
        }

    # ------------------------------------------------------------------
    # Persistence shortcut
    # ------------------------------------------------------------------

    async def _save_and_refresh(
        self,
        model: TModel,
        refresh_attrs: Optional[list[str]] = None,
    ) -> TModel:
        self._session.add(model)
        await self._session.flush()
        await self._session.commit()
        kwargs: dict[str, Any] = {}
        if refresh_attrs is not None:
            kwargs["attribute_names"] = refresh_attrs
        await self._session.refresh(model, **kwargs)
        return model

    # ------------------------------------------------------------------
    # Entity mapping (must be implemented by subclasses)
    # ------------------------------------------------------------------

    @staticmethod
    @abstractmethod
    def _to_entity(model: Any) -> TEntity:
        ...
