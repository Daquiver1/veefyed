"""Setting up configs."""

# Third party import
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

# Project configs
PROJECT_NAME = "Veefyed Backend"
VERSION = "1.0"
API_PREFIX = "/api/v1"

# Environment
ENV = config("ENV", cast=str, default="DEV")

# Database
POSTGRES_USERNAME = config("POSTGRES_USERNAME", cast=str, default="")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=str, default="")
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="")
POSTGRES_DB = config("POSTGRES_DB", cast=str, default="")

# Redis
REDIS_PASSWORD = config("REDIS_PASSWORD", cast=str, default=None)
REDIS_SESSION_PREFIX = config("REDIS_SESSION_PREFIX", cast=str, default="quiverfood")
SESSION_EXPIRY_HOURS = config("SESSION_EXPIRY_HOURS", cast=int, default=24)


if ENV == "PROD":
    DATABASE_URL = config("PROD_DATABASE_URL", cast=str, default="")
    FRONTEND_URL = config("PROD_FRONTEND_URL", cast=str, default="")
    REDIS_HOST = config("REDIS_HOST_PROD", cast=str)
    REDIS_PORT = config("REDIS_PORT_PROD", cast=int)
    REDIS_URL = f"rediss://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
else:
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    FRONTEND_URL = config("DEV_FRONTEND_URL", cast=str, default="")
    REDIS_HOST = config("REDIS_HOST_DEV", cast=str, default="localhost")
    REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=60
)
REFRESH_TOKEN_EXPIRE_DAYS = config("REFRESH_TOKEN_EXPIRE_DAYS", cast=int, default=7)
SECRET_KEY = config("SECRET_KEY", cast=str, default="")
ALGORITHM = config("ALGORITHM", cast=str, default="HS256")


# AWS S3 configs
S3_BUCKET_NAME = config("S3_BUCKET_NAME", cast=str, default="")
S3_ACCESS_KEY_ID = config("S3_ACCESS_KEY_ID", cast=str, default="")
S3_SECRET_ACCESS_KEY = config("S3_SECRET_ACCESS_KEY", cast=Secret, default="")
S3_REGION = config("S3_REGION", cast=str, default=" ")

# Groq
GROQ_API_KEY = config("GROQ_API_KEY", cast=str, default="")
GROQ_MODEL = config("GROQ_MODEL_ID", cast=str, default="")
GROQ_TEMPERATURE = config("GROQ_TEMPERATURE", cast=float, default=0.6)

# Gemini
GEMINI_API_KEY = config("GEMINI_API_KEY2", cast=str, default="")
GEMINI_MODEL = config("GEMINI_MODEL_ID", cast=str, default="")
GEMINI_TEMPERATURE = config("GEMINI_TEMPERATURE", cast=float, default=0.6)
