import bcrypt
from app.core.config import BCRYPT_ROUNDS

def hash_password(password: str) -> str:
    password = password.strip()
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.strip().encode("utf-8"),
        hashed_password.encode("utf-8")
    )
