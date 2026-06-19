import logging
from functools import lru_cache

import jwt
from fastapi import Header, HTTPException
from jwt import PyJWKClient

from app.config import settings

logger = logging.getLogger(__name__)


_AUDIENCE = "authenticated"


@lru_cache(maxsize=1)
def _jwk_client() -> PyJWKClient:
    return PyJWKClient(f"{settings.supabase_url}/auth/v1/.well-known/jwks.json")


async def get_current_user(authorization: str = Header(default="")) -> str:
    """Verify the Supabase access token and return the user id (the `sub` claim)."""
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    try:
        alg = jwt.get_unverified_header(token).get("alg")
        if alg == "HS256":
            if not settings.supabase_jwt_secret:
                raise RuntimeError("supabase_jwt_secret not set")
            key = settings.supabase_jwt_secret
        else:
            key = _jwk_client().get_signing_key_from_jwt(token).key

        claims = jwt.decode(
            token, key, algorithms=["ES256", "HS256"], audience=_AUDIENCE
        )
    except jwt.PyJWTError as exc:
        logger.info("token rejected: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    except Exception:
        logger.exception("auth verification error")
        raise HTTPException(status_code=500, detail="Auth not configured")

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing subject")
    return user_id