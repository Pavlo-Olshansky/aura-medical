from datetime import datetime

from pydantic import BaseModel


class ReferenceCreate(BaseModel):
    name: str


class ReferenceUpdate(BaseModel):
    name: str


class ReferenceResponse(BaseModel):
    id: int
    name: str
    created: datetime
    updated: datetime

    model_config = {"from_attributes": True}
