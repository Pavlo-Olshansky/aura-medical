from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Request

from app.application.auth_service import AuthAppService
from app.application.biomarker_reference_service import BiomarkerReferenceAppService
from app.application.dashboard_service import DashboardAppService
from app.application.health_metric_service import HealthMetricAppService
from app.application.lab_result_service import LabResultAppService
from app.application.metric_type_service import MetricTypeAppService
from app.application.reference_service import ReferenceAppService
from app.application.timeline_service import TimelineAppService
from app.application.treatment_service import TreatmentAppService
from app.application.weather_service import WeatherAppService
from app.application.vaccination_service import VaccinationAppService
from app.application.visit_service import VisitAppService
from app.config import settings
from app.domain.entities import User
from app.domain.exceptions import AuthenticationError, EntityNotFound
from app.infrastructure.database import get_session
from app.infrastructure.jwt_token_service import JoseTokenService
from app.infrastructure.local_document_storage import LocalDocumentStorage
from app.infrastructure.models.reference import ClinicModel, CityModel, PositionModel, ProcedureModel
from app.infrastructure.repositories.biomarker_reference_repository import SqlAlchemyBiomarkerReferenceRepository
from app.infrastructure.repositories.health_metric_repository import SqlAlchemyHealthMetricRepository
from app.infrastructure.repositories.lab_result_repository import SqlAlchemyLabResultRepository
from app.infrastructure.repositories.metric_type_repository import SqlAlchemyMetricTypeRepository
from app.infrastructure.repositories.reference_repository import SqlAlchemyReferenceRepository
from app.infrastructure.repositories.treatment_repository import SqlAlchemyTreatmentRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.repositories.vaccination_repository import SqlAlchemyVaccinationRepository
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


def get_biomarker_reference_service(session: AsyncSession = Depends(get_session)) -> BiomarkerReferenceAppService:
    return BiomarkerReferenceAppService(SqlAlchemyBiomarkerReferenceRepository(session))


def get_metric_type_service(session: AsyncSession = Depends(get_session)) -> MetricTypeAppService:
    return MetricTypeAppService(SqlAlchemyMetricTypeRepository(session))


def get_lab_result_service(session: AsyncSession = Depends(get_session)) -> LabResultAppService:
    return LabResultAppService(SqlAlchemyLabResultRepository(session))


def get_health_metric_service(session: AsyncSession = Depends(get_session)) -> HealthMetricAppService:
    return HealthMetricAppService(
        SqlAlchemyHealthMetricRepository(session),
        SqlAlchemyMetricTypeRepository(session),
    )


def get_vaccination_service(session: AsyncSession = Depends(get_session)) -> VaccinationAppService:
    storage = LocalDocumentStorage(settings.DOCUMENTS_DIR, session)
    return VaccinationAppService(SqlAlchemyVaccinationRepository(session), storage)


def get_timeline_service(session: AsyncSession = Depends(get_session)) -> TimelineAppService:
    return TimelineAppService(
        SqlAlchemyVisitRepository(session),
        SqlAlchemyTreatmentRepository(session),
        SqlAlchemyLabResultRepository(session),
        SqlAlchemyVaccinationRepository(session),
    )


def get_dashboard_service(session: AsyncSession = Depends(get_session)) -> DashboardAppService:
    return DashboardAppService(
        SqlAlchemyVisitRepository(session),
        SqlAlchemyTreatmentRepository(session),
        session=session,
    )


def get_weather_service(request: Request) -> WeatherAppService:
    return WeatherAppService(
        client=request.app.state.skypulse,
        city=settings.WEATHER_CITY,
    )
