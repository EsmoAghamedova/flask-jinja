from datetime import datetime, timedelta
from flask import current_app
import jwt
import secrets

def generate_token(user_id, purpose, expires_in=86400):
    payload = {
        "user_id": user_id,
        "purpose": purpose,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
    }

    jti = None
    if purpose == "reset":
        jti = secrets.token_urlsafe(16)
        payload["jti"] = jti

    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token, jti

def read_token(token, expected_purpose):
    try:
        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
        if payload.get("purpose") != expected_purpose:
            return None
        return payload.get("user_id")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
