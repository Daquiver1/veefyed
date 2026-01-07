FROM python:3.11.8-slim-bookworm AS build-stage

WORKDIR /veefyed
RUN mkdir -p logs 

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONBUFFERED=1

RUN apt-get update \
  && apt-get -y install netcat-openbsd gcc libpq-dev  \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ["chmod", "+x", "./run.sh"]
CMD ["./run.sh"]
