from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

# Password Hashing Configuration

# We use Argon2id, the modern standard for password hashing, recommended by OWASP.
# Passlib's CryptContext allows us to easily manage hashing schemes.
# If we need to upgrade hashing parameters or add a new scheme (e.g., bcrypt),
# passlib will automatically handle rehashing old passwords upon verification.

# Argon2id parameters based on OWASP minimum recommendations:
# m = 19 MiB (memory cost) 19 * 1024 = 19456 KiB
# t = 2 (time cost / iterations)
# p = 1 (parallelism)

pwd_context = CryptContext(
    schemes=["argon2"], # Default and only scheme is argon2
    deprecated="auto", # Automatically mark old schemes as deprecated if new ones are added
    argon2__type="ID",
    argon2__memory_cost=19456,  # 19 MiB
    argon2__time_cost=2,
    argon2__parallelism=1,
)

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)

def create_access_token(subject: str) -> str:
    # Set the token expiration time
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    # Payload to encode
    to_encode = {"sub": subject, "exp": expire}
    # Encode the token using the secret key and algorithm from settings
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload.get("sub")
    except JWTError:
        return None