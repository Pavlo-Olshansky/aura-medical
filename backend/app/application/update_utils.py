from __future__ import annotations

from pydantic import BaseModel


def apply_update(entity, command: BaseModel, exclude: set[str] | None = None) -> None:
    """Apply non-None fields from a Pydantic command to a domain entity.

    Uses model_dump(exclude_unset=True) to only update fields that were
    explicitly provided in the request, preserving existing values for
    omitted fields.
    """
    updates = command.model_dump(exclude_unset=True)
    if exclude:
        for key in exclude:
            updates.pop(key, None)
    for field, value in updates.items():
        setattr(entity, field, value)
