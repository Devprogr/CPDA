import os

class Config:
    SECRET_KEY = os.getenv("APP_SECRET_KEY", "change-me")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True

    MAX_CONTENT_LENGTH = 6 * 1024 * 1024  # 6MB