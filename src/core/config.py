"""Setting up configs."""

# Third party import
from starlette.config import Config

config = Config(".env")

# Project configs
PROJECT_NAME = "Veefyed Backend"
VERSION = "1.0"
API_PREFIX = "/api/v1"

# Environment
ENV = config("ENV", cast=str, default="DEV")


# Redis
REDIS_PASSWORD = config("REDIS_PASSWORD", cast=str, default=None)
REDIS_SESSION_PREFIX = config("REDIS_SESSION_PREFIX", cast=str, default="quiverfood")
SESSION_EXPIRY_HOURS = config("SESSION_EXPIRY_HOURS", cast=int, default=24)


if ENV == "PROD":
    DATABASE_URL = config("PROD_DATABASE_URL", cast=str, default="")
    REDIS_HOST = config("REDIS_HOST_PROD", cast=str)
    REDIS_PORT = config("REDIS_PORT_PROD", cast=int)
    REDIS_URL = f"rediss://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
else:
    DATABASE_URL = config("DATABASE_URL", cast=str, default="")
    REDIS_HOST = config("REDIS_HOST_DEV", cast=str, default="localhost")
    REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"


# Groq
GROQ_API_KEY = config("GROQ_API_KEY", cast=str, default="")
GROQ_MODEL = config("GROQ_MODEL_ID", cast=str, default="")
GROQ_TEMPERATURE = config("GROQ_TEMPERATURE", cast=float, default=0.6)

# Gemini
GEMINI_API_KEY = config("GEMINI_API_KEY2", cast=str, default="")
GEMINI_MODEL = config("GEMINI_MODEL_ID", cast=str, default="")
GEMINI_TEMPERATURE = config("GEMINI_TEMPERATURE", cast=float, default=0.6)

# Storage
UPLOAD_DIR = config("UPLOAD_DIR", cast=str, default="uploads/images")
