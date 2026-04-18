from dataclasses import dataclass
from typing import Any, Optional, Sequence, Type

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.application.pagination import calculate_pages
from app.domain.entities import User
from app.domain.exceptions import DomainError, EntityNotFound
from app.schemas.pagination import PaginatedResponse


@dataclass
class QueryParam:
    name: str
    type: type
    default: Any


def create_crud_router(
    *,
    prefix: str,
    tags: Sequence[str],
    response_schema: Type[BaseModel],
    list_item_schema: Type[BaseModel],
    create_schema: Optional[Type[BaseModel]] = None,
    update_schema: Optional[Type[BaseModel]] = None,
    get_service: Any,
    get_current_user: Any,
    list_params: Optional[list[QueryParam]] = None,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=list(tags))
    list_response_model = PaginatedResponse[list_item_schema]  # type: ignore[valid-type]

    # ── LIST ──────────────────────────────────────────────────────────

    if list_params:
        # FastAPI inspects the function signature to discover query parameters,
        # so we build the signature dynamically to include custom filters.
        import inspect

        param_names = [p.name for p in list_params]

        base_params = [
            inspect.Parameter(
                "page",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Query(1, ge=1),
                annotation=int,
            ),
            inspect.Parameter(
                "size",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Query(20, ge=1, le=100),
                annotation=int,
            ),
            inspect.Parameter(
                "sort",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Query("-id"),
                annotation=str,
            ),
        ]

        filter_params = []
        for qp in list_params:
            filter_params.append(
                inspect.Parameter(
                    qp.name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=qp.default,
                    annotation=qp.type,
                )
            )

        dep_params = [
            inspect.Parameter(
                "current_user",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(get_current_user),
                annotation=User,
            ),
            inspect.Parameter(
                "service",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(get_service),
            ),
        ]

        all_params = base_params + filter_params + dep_params

        async def _list_handler(**kwargs: Any) -> Any:
            page = kwargs["page"]
            size = kwargs["size"]
            sort = kwargs["sort"]
            current_user = kwargs["current_user"]
            service = kwargs["service"]
            filters = {name: kwargs[name] for name in param_names}
            items, total = await service.list(
                current_user.id, page=page, size=size, sort=sort, **filters,
            )
            pages = calculate_pages(total, size)
            return list_response_model(
                items=[list_item_schema.model_validate(i) for i in items],
                total=total,
                page=page,
                size=size,
                pages=pages,
            )

        _list_handler.__signature__ = inspect.Signature(all_params)  # type: ignore[attr-defined]
        router.add_api_route(
            "/",
            _list_handler,
            methods=["GET"],
            response_model=list_response_model,
        )
    else:

        @router.get("/", response_model=list_response_model)
        async def list_items(
            page: int = Query(1, ge=1),
            size: int = Query(20, ge=1, le=100),
            sort: str = Query("-id"),
            current_user: User = Depends(get_current_user),
            service=Depends(get_service),
        ) -> Any:
            items, total = await service.list(
                current_user.id, page=page, size=size, sort=sort,
            )
            pages = calculate_pages(total, size)
            return list_response_model(
                items=[list_item_schema.model_validate(i) for i in items],
                total=total,
                page=page,
                size=size,
                pages=pages,
            )

    # ── GET ───────────────────────────────────────────────────────────

    @router.get("/{item_id}", response_model=response_schema)
    async def get_item(
        item_id: int,
        current_user: User = Depends(get_current_user),
        service=Depends(get_service),
    ) -> Any:
        try:
            entity = await service.get_by_id(item_id, current_user.id)
        except EntityNotFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Not found",
            )
        return response_schema.model_validate(entity)

    # ── CREATE ────────────────────────────────────────────────────────

    if create_schema is not None:
        _create_schema = create_schema  # capture for closure

        @router.post("/", response_model=response_schema, status_code=201)
        async def create_item(
            data: _create_schema,  # type: ignore[valid-type]
            current_user: User = Depends(get_current_user),
            service=Depends(get_service),
        ) -> Any:
            try:
                entity = await service.create(current_user.id, data)
            except EntityNotFound:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Not found",
                )
            except DomainError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(exc),
                )
            return response_schema.model_validate(entity)

    # ── UPDATE ────────────────────────────────────────────────────────

    if update_schema is not None:
        _update_schema = update_schema  # capture for closure

        @router.put("/{item_id}", response_model=response_schema)
        async def update_item(
            item_id: int,
            data: _update_schema,  # type: ignore[valid-type]
            current_user: User = Depends(get_current_user),
            service=Depends(get_service),
        ) -> Any:
            try:
                entity = await service.update(item_id, current_user.id, data)
            except EntityNotFound:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Not found",
                )
            except DomainError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(exc),
                )
            return response_schema.model_validate(entity)

    # ── DELETE ────────────────────────────────────────────────────────

    @router.delete("/{item_id}", status_code=204)
    async def delete_item(
        item_id: int,
        current_user: User = Depends(get_current_user),
        service=Depends(get_service),
    ) -> None:
        try:
            await service.delete(item_id, current_user.id)
        except EntityNotFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Not found",
            )

    return router
