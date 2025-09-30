import random
import string

import bcrypt


def hash_password(plain_password: str) -> str:
    """Hash password using bcrypt with 12 salt rounds"""
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def is_valid_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def generate_random_password() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=12))
