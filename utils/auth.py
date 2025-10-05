import secrets
from datetime import datetime, timedelta

def generate_token(length=32):
    return secrets.token_urlsafe(length)

def generate_session_token():
    return secrets.token_urlsafe(64)

def get_expiry_time(minutes=15):
    return datetime.utcnow() + timedelta(minutes=minutes)

def is_token_expired(expires_at):
    return datetime.utcnow() > expires_at
