from app.domain.entities import User
from app.domain.exceptions import AuthenticationError, EntityNotFound
from app.domain.services import PasswordService
from app.domain.repositories import UserRepository, TokenService


class AuthAppService:
    def __init__(self, repo: UserRepository, tokens: TokenService):
        self._repo = repo
        self._tokens = tokens

    async def login(self, username: str, password: str) -> tuple[str, str]:
        user = await self._repo.get_by_username(username)
        if not user or not PasswordService.verify(password, user.password_hash):
            raise AuthenticationError("Invalid username or password")
        user.ensure_active()
        return self._tokens.create_access_token(user.id), self._tokens.create_refresh_token(user.id)

    async def refresh(self, token: str) -> tuple[str, str]:
        try:
            user_id = self._tokens.verify_token(token, expected_type="refresh")
        except ValueError:
            raise AuthenticationError("Invalid or expired refresh token")
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found or inactive")
        user.ensure_active()
        return self._tokens.create_access_token(user.id), self._tokens.create_refresh_token(user.id)

    async def get_current_user(self, user_id: int) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise EntityNotFound("User not found")
        user.ensure_active()
        return user
