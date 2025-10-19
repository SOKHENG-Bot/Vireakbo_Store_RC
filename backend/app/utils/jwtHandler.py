from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from pydantic import BaseModel


class TokenData(BaseModel):
    userId: str
    phoneNumber: str
    fullName: str
    expiresAt: datetime


class JWTHandler:
    """Utility class for handling JWT operations"""

    def __init__(self, secretKey: str, algorithm: str) -> None:
        self.secretKey = secretKey
        self.algorithm = algorithm

    def encodeToken(
        self, payload: Dict[str, Any], expiresDelta: Optional[timedelta] = None
    ) -> str:
        """Encode a JWT token with an expiration time"""

        toEncode = payload.copy()
        if expiresDelta:
            expire = datetime.now(timezone.utc) + expiresDelta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        toEncode.update(
            {"exp": expire, "iat": datetime.now(timezone.utc), "type": "access"}
        )

        encodedJwt = jwt.encode(toEncode, self.secretKey, algorithm=self.algorithm)
        return encodedJwt

    def decodeToken(self, token: str) -> TokenData:
        """Decode a JWT token and return the token data"""
        try:
            payload = jwt.decode(token, self.secretKey, algorithms=[self.algorithm])
            phoneNumber = payload.get("phoneNumber")
            exp = payload.get("exp")

            if not phoneNumber or not exp:
                raise ValueError("Invalid token payload")

            return TokenData(
                userId=str(payload.get("userId")),
                phoneNumber=phoneNumber,
                fullName=payload.get("fullName") or "",
                expiresAt=datetime.fromtimestamp(exp, tz=timezone.utc),
            )
        except ExpiredSignatureError:
            raise ValueError("Token has expired")
        except JWTError as e:
            raise ValueError(f"Token decode error: {e}")
