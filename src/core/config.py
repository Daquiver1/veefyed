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

# Storage
UPLOAD_DIR = config("UPLOAD_DIR", cast=str, default="uploads/images")
