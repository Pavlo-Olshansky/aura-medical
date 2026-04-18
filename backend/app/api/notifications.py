from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.application.notification_service import NotificationAppService
from app.domain.entities import User
from app.infrastructure.database import get_session
from app.schemas.notification import DismissRequest, ReminderResponse, RemindersListResponse

router = APIRouter()


def get_notification_service(session: AsyncSession = Depends(get_session)) -> NotificationAppService:
    return NotificationAppService(session)


@router.get("/", response_model=RemindersListResponse)
async def get_reminders(
    current_user: User = Depends(get_current_user),
    service: NotificationAppService = Depends(get_notification_service),
):
    items = await service.get_reminders(current_user.id)
    return RemindersListResponse(
        items=[ReminderResponse(**r) for r in items],
        count=len(items),
    )


@router.post("/dismiss", status_code=204)
async def dismiss_reminder(
    body: DismissRequest,
    current_user: User = Depends(get_current_user),
    service: NotificationAppService = Depends(get_notification_service),
):
    await service.dismiss(current_user.id, body.entity_type, body.entity_id, body.reminder_type)
