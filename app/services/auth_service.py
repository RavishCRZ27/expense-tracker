from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User
from app.config import get_settings

settings = get_settings()

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Predefined Admin ──────────────────────────────────────────────────────
ADMIN_USERNAME = "Ravish"
ADMIN_EMAIL = "ravishpandey27@gmail.com"
ADMIN_PASSWORD = "ravish123"
ADMIN_FULL_NAME = "Ravish Pandey"


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token. Returns payload or None."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user by username and password. Returns User or None."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, username: str, email: str, password: str, full_name: str = None) -> User:
    """Create a new user account."""
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Look up a user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Look up a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Look up a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def seed_admin(db: Session) -> None:
    """Create the predefined admin user if not already present."""
    existing = db.query(User).filter(
        (User.username == ADMIN_USERNAME) | (User.email == ADMIN_EMAIL)
    ).first()
    if not existing:
        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            full_name=ADMIN_FULL_NAME,
            is_admin=True,
        )
        db.add(admin)
        db.commit()
