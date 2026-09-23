import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.database import SessionLocal, UserRecord
from app.schemas.auth import UserRegister, UserOut

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def create_access_token(self, user_id: str) -> str:
        payload = {
            "sub": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload.get("sub")
        except jwt.PyJWTError:
            return None

    def register(self, req: UserRegister) -> UserOut:
        db = SessionLocal()
        try:
            existing = db.query(UserRecord).filter(UserRecord.email == req.email).first()
            if existing:
                raise ValueError("An account with this email already exists.")
            user = UserRecord(
                id=f"usr_{uuid.uuid4().hex[:12]}",
                email=req.email,
                name=req.name,
                hashed_password=self.hash_password(req.password),
            )
            db.add(user)
            db.commit()
            return UserOut(id=user.id, email=user.email, name=user.name)
        finally:
            db.close()

    def authenticate(self, email: str, password: str) -> Optional[UserOut]:
        db = SessionLocal()
        try:
            user = db.query(UserRecord).filter(UserRecord.email == email).first()
            if not user or not self.verify_password(password, user.hashed_password):
                return None
            return UserOut(id=user.id, email=user.email, name=user.name)
        finally:
            db.close()

    def get_user(self, user_id: str) -> Optional[UserOut]:
        db = SessionLocal()
        try:
            user = db.get(UserRecord, user_id)
            return UserOut(id=user.id, email=user.email, name=user.name) if user else None
        finally:
            db.close()


auth_service = AuthService()
