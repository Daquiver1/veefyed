# Veefyed - Skin Analysis API

A FastAPI-based REST API service for uploading images and analyzing skin conditions using AI/ML models.

## Table of Contents

- [Features](#features)
- [How to Run the Service](#how-to-run-the-service)
- [Available Endpoints](#available-endpoints)
- [Assumptions Made](#assumptions-made)
- [Production Improvements](#production-improvements)

## Features

- **Image Upload & Storage**: Upload images with validation (JPEG/PNG, max 5MB)
- **Skin Analysis**: AI-powered skin type detection and issue identification
- **API Key Authentication**: Scope-based access control (upload, analyze)
- **Async Operations**: Built with async/await for high performance
- **Database Migrations**: Alembic for database schema management
- **Caching**: Redis integration for session management
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Type Safety**: Full type hints and Pydantic validation

## How to Run the Service

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**

```bash

git clone https://github.com/Daquiver1/veefyed.git
cd veefyed
```

1. **Set up environment variables**

```bash
cp .env.template .env
# Edit .env with your configuration
```

1. **Build and run with Docker Compose**

```bash
docker-compose up --build
```

1. **Run database migrations**

```bash
docker-compose exec web alembic upgrade head
```

1. **Access the API**

- API: <http://localhost:8008>
- Interactive Docs: <http://localhost:8008/docs>

### Running Tests

1. **Run test**

```bash
docker-compose exec web pytest
```

## Available Endpoints

### Base URL: `http://localhost:8008/api/v1`

**API Key Management**

- `POST /api/v1/api-keys` - Create API key
- `GET /api/v1/api-keys/me` - Get current API key info
- `GET /api/v1/api-keys/{api_key}` - Get API key by value

**Image Management**

- `POST /api/v1/images` - Upload image
- `GET /api/v1/images/{image_id}` - Get image metadata

**Image Analysis**

- `POST /api/v1/image-analysis/{image_id}/analyze` - Create analysis
- `GET /api/v1/image-analysis/{image_id}/analysis` - Get latest analysis

**Health & Status**

- `GET /health` - Health check
- `GET /` - Root endpoint

> **Note**: Full API documentation available at `http://localhost:8008/docs`

## Assumptions Made

### Image Uploads

- [ ] Assumed image won't be uploaded in batches.
- [ ] Assumed basic validation (file type, size) is sufficient for demo purposes.

### Api Key Management

- [ ] Assumed api keys are long-lived without expiration for simplicity.
- [ ] Assumed no user accounts; api keys are the sole auth mechanism.

## Production Improvements

### Security & Authentication

- [ ] **OAuth2/JWT Authentication**: Replace API keys with OAuth2 flow
- [ ] **API Key Rotation**: Implement key rotation and expiration
- [ ] **Rate Limiting**: Add per-key rate limits using Redis
- [ ] **CORS Configuration**: Restrict to specific domains

### Image Storage & Processing

- [ ] **Cloud Storage**: Migrate to S3/GCS/Azure Blob Storage
- [ ] **Image Optimization**: Compress/resize on upload

### AI/ML Integration

- [ ] **Real Model Integration**: Replace mock with actual AI model
- [ ] **Model Versioning**: Track and manage model versions

### Database & Performance

- [ ] **PostgreSQL**: Migrate from SQLite
- [ ] **Pagination**: Implement cursor-based pagination
- [ ] **Caching**: Redis caching for frequent queries

### Observability & Monitoring

- [ ] **APM**: Application Performance Monitoring (DataDog, New Relic)
- [ ] **Metrics**: Prometheus/Grafana for metrics
- [ ] **Error Tracking**: Sentry for error monitoring

### API Improvements

- [ ] **Webhooks**: Event notifications for analysis completion
- [ ] **Batch Operations**: Bulk upload/analysis
