"""
User authentication and Profile
Core security helpers: password hashing(passlib/bcrypt) and JWT (python.json)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
from jose import jwt, JWTError
from passlib.context import CryptContext

from backend.config import settings

#bcrypt handles hashing + salting automatically.
# "bcrypt_sha256" is listed too (verify-only, via deprecated="auto") so any
# accounts whose hash was created with that scheme can still log in - only
# "bcrypt" is used for hashing *new* passwords.
pwd_context = CryptContext(schemes=["bcrypt", "bcrypt_sha256"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """Hash a plain password before storing it the DB."""
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against the stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None ) -> str:
    """
    Create a signed JWT containing `data` (e.g. {"sub" : user_id}).
    Adds an expiry claim automatically.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token:str) -> Optional[dict]:
    """
    Decode and verify a jwt. Returns the payload dict if valid, None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
    
def generate_verification_token() -> str:
    """
    Generate a secure random, url-safe token used for email verification links.
    This is NOT a JWT - just a random opaque string stored in the DB and matches on verify.
    """
    return secrets.token_urlsafe(32)


def parse_device_info(user_agent: Optional[str]) -> str:
    """
    Very lightweight User-Agent -> human-readable device label, e.g.
    "Chrome on Windows". Good enough for showing users a recognizable list of
    their own sessions - not meant to be a full UA-parsing library.
    """
    if not user_agent:
        return "Unknown device"

    ua = user_agent.lower()

    if "edg/" in ua:
        browser = "Edge"
    elif "chrome/" in ua and "chromium" not in ua:
        browser = "Chrome"
    elif "firefox/" in ua:
        browser = "Firefox"
    elif "safari/" in ua and "chrome/" not in ua:
        browser = "Safari"
    else:
        browser = "Unknown browser"

    if "windows" in ua:
        os_name = "Windows"
    elif "mac os" in ua or "macintosh" in ua:
        os_name = "macOS"
    elif "android" in ua:
        os_name = "Android"
    elif "iphone" in ua or "ipad" in ua:
        os_name = "iOS"
    elif "linux" in ua:
        os_name = "Linux"
    else:
        os_name = "Unknown OS"

    return f"{browser} on {os_name}"