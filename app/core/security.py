from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    TODO : hacher le mot de passe en clair avec pwd_context.
    Indice : pwd_context.hash(...)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    TODO : vérifier que plain_password correspond bien à hashed_password.
    Indice : pwd_context.verify(...) -> retourne un bool
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    TODO : créer un JWT signé contenant `data` (ex: {"sub": user.email}),
    avec une expiration (utiliser JWT_EXPIRE_MINUTES).

    Étapes :
    1. Copier `data` dans un dict `to_encode` (ne jamais muter l'original)
    2. Calculer `expire` = maintenant (UTC) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    3. Ajouter to_encode["exp"] = expire
    4. jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    TODO : décoder et vérifier le token, retourner le payload (dict).
    Si le token est invalide/expiré, jwt.decode lève une exception
    (jwt.ExpiredSignatureError, jwt.InvalidTokenError) — laisse-la remonter,
    on la gérera dans dependencies.py.

    Indice : jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    """
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
