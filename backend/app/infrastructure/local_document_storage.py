import os
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession



class LocalDocumentStorage:
    def __init__(self, documents_dir: str, session: Optional[AsyncSession] = None):
        self._documents_dir = documents_dir
        self._session = session

    async def save(self, filename: str, content: bytes, visit_date: datetime, procedure_id: Optional[int]) -> str:
        year = visit_date.year

        procedure_name = "інше"
        if procedure_id and self._session:
            from app.infrastructure.models.reference import ProcedureModel
            result = await self._session.execute(
                select(ProcedureModel).where(ProcedureModel.id == procedure_id)
            )
            proc = result.scalar_one_or_none()
            if proc:
                procedure_name = proc.name

        subdir = f"{year}_{procedure_name}"
        docs_dir = os.path.join(self._documents_dir, subdir)
        os.makedirs(docs_dir, exist_ok=True)

        filepath = os.path.join(docs_dir, filename)
        if os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            filepath = os.path.join(docs_dir, filename)

        with open(filepath, "wb") as f:
            f.write(content)

        return os.path.join("documents", subdir, filename)

    def get_path(self, relative_path: str) -> str:
        docs_parent = os.path.dirname(self._documents_dir)
        return os.path.join(docs_parent, relative_path)
