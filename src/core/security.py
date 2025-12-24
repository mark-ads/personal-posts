from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Захешировать пароль."""
    return password_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Верифицировать пароль."""
    return password_context.verify(password, hashed)

