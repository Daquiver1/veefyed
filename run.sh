#!/bin/bash
# run.sh

alembic upgrade head

gunicorn -w 1 -k uvicorn.workers.UvicornWorker src.api.main:app --bind 0.0.0.0:${PORT:-8080}