from datetime import datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings

ALGORITHM = "HS256"


class JoseTokenService:
    def create_access_token(self, user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode({"sub": str(user_id), "exp": expire, "type": "access"}, settings.SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return jwt.encode({"sub": str(user_id), "exp": expire, "type": "refresh"}, settings.SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str, expected_type: str = "access") -> int:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        except InvalidTokenError:
            raise ValueError("Invalid token")
        if payload.get("type") != expected_type:
            raise ValueError(f"Expected {expected_type} token")
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token payload")
        return int(user_id)
