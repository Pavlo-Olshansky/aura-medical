from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth_service import AuthAppService
from app.application.dashboard_service import DashboardAppService
from app.application.reference_service import ReferenceAppService
from app.application.treatment_service import TreatmentAppService
from app.application.visit_service import VisitAppService
from app.config import settings
from app.domain.entities import User
from app.domain.exceptions import AuthenticationError, EntityNotFound
from app.infrastructure.database import get_session
from app.infrastructure.jwt_token_service import JoseTokenService
from app.infrastructure.local_document_storage import LocalDocumentStorage
from app.infrastructure.models.reference import ClinicModel, CityModel, PositionModel, ProcedureModel
from app.infrastructure.repositories.reference_repository import SqlAlchemyReferenceRepository
from app.infrastructure.repositories.treatment_repository import SqlAlchemyTreatmentRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.repositories.visit_repository import SqlAlchemyVisitRepository

security = HTTPBearer()
_token_service = JoseTokenService()


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthAppService:
    return AuthAppService(SqlAlchemyUserRepository(session), _token_service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthAppService = Depends(get_auth_service),
) -> User:
    try:
        user_id = _token_service.verify_token(credentials.credentials, expected_type="access")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    try:
        return await auth_service.get_current_user(user_id)
    except (EntityNotFound, AuthenticationError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")


def get_visit_service(session: AsyncSession = Depends(get_session)) -> VisitAppService:
    repo = SqlAlchemyVisitRepository(session)
    storage = LocalDocumentStorage(settings.DOCUMENTS_DIR, session)
    return VisitAppService(repo, storage)


def get_treatment_service(session: AsyncSession = Depends(get_session)) -> TreatmentAppService:
    return TreatmentAppService(SqlAlchemyTreatmentRepository(session))


def get_position_service(session: AsyncSession = Depends(get_session)) -> ReferenceAppService:
    return ReferenceAppService(SqlAlchemyReferenceRepository(session, PositionModel, "position_id"))


def get_procedure_service(session: AsyncSession = Depends(get_session)) -> ReferenceAppService:
    return ReferenceAppService(SqlAlchemyReferenceRepository(session, ProcedureModel, "procedure_id"))


def get_clinic_service(session: AsyncSession = Depends(get_session)) -> ReferenceAppService:
    return ReferenceAppService(SqlAlchemyReferenceRepository(session, ClinicModel, "clinic_id"))


def get_city_service(session: AsyncSession = Depends(get_session)) -> ReferenceAppService:
    return ReferenceAppService(SqlAlchemyReferenceRepository(session, CityModel, "city_id"))


def get_dashboard_service(session: AsyncSession = Depends(get_session)) -> DashboardAppService:
    return DashboardAppService(
        SqlAlchemyVisitRepository(session),
        SqlAlchemyTreatmentRepository(session),
    )
