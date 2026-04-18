from __future__ import annotations

from dataclasses import fields
from typing import Any

from pydantic import BaseModel


def apply_update(entity: Any, command: Any, exclude: set[str] | None = None) -> None:
    """Apply non-None fields from a command to a domain entity.

    Supports both Pydantic BaseModel (model_dump) and dataclass commands.
    For dataclasses, updates fields whose values differ from the dataclass
    default (i.e. are not None).
    """
    if isinstance(command, BaseModel):
        updates = command.model_dump(exclude_unset=True)
    else:
        # dataclass command — include only fields that are not None
        updates = {f.name: getattr(command, f.name) for f in fields(command) if getattr(command, f.name) is not None}
    if exclude:
        for key in exclude:
            updates.pop(key, None)
    for field_name, value in updates.items():
        setattr(entity, field_name, value)
