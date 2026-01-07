# Veefyed - Skin Analysis API

A FastAPI-based REST API service for uploading images and analyzing skin conditions using AI/ML models.

## Table of Contents

- [Features](#features)
- [How to Run the Service](#how-to-run-the-service)
- [Available Endpoints](#available-endpoints)
- [Project Structure](#project-structure)
- [Testing](#testing)
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
git clone <repository-url>
cd veefyed
```

2. **Set up environment variables**

```bash
cp .env.template .env
# Edit .env with your configuration
```

3. **Build and run with Docker Compose**

```bash
docker-compose up --build
```

4. **Run database migrations**

```bash
docker-compose exec web alembic upgrade head
```

5. **Access the API**

- API: http://localhost:8008
- Interactive Docs: http://localhost:8008/docs
- ReDoc: http://localhost:8008/redoc

### Local Development

1. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing
```

3. **Set up environment**

```bash
cp .env.template .env
# Configure DATABASE_URL and REDIS settings
```

4. **Run migrations**

```bash
alembic upgrade head
```

5. **Start the server**

```bash
uvicorn src.api.main:app --reload --port 8000
```

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test types
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests only
```

## Available Endpoints

### Base URLs

- **Development**: `http://localhost:8008/api/v1`
- **Health Check**: `http://localhost:8008/health`

### API Key Management

#### Create API Key

```http
POST /api/v1/api-keys
Content-Type: application/json

{
  "name": "My Application",
  "scopes": ["upload", "analyze"]
}

Response: 201 Created
{
  "api_key": "generated-api-key-string",
  "message": "Store this API key securely; it will not be shown again."
}
```

#### Get Current API Key Info

```http
GET /api/v1/api-keys/me
X-API-Key: your-api-key

Response: 200 OK
{
  "id": "uuid",
  "name": "My Application",
  "scopes": ["upload", "analyze"],
  "created_at": "2026-01-07T10:00:00",
  "updated_at": "2026-01-07T10:00:00"
}
```

### Image Management

#### Upload Image

```http
POST /api/v1/images
X-API-Key: your-api-key
Content-Type: multipart/form-data

Form Data:
- image: (file) [JPEG or PNG, max 5MB]

Response: 201 Created
{
  "id": "image-uuid",
  "content_type": "image/jpeg",
  "file_size": 1024000,
  "storage_path": "uploads/images/uuid.jpg",
  "created_at": "2026-01-07T10:00:00",
  "updated_at": "2026-01-07T10:00:00"
}
```

**Requirements:**

- Valid API key with `upload` scope
- Image format: JPEG or PNG
- Maximum file size: 5MB

#### Get Image Metadata

```http
GET /api/v1/images/{image_id}
X-API-Key: your-api-key

Response: 200 OK
{
  "id": "image-uuid",
  "content_type": "image/jpeg",
  "file_size": 1024000,
  "storage_path": "uploads/images/uuid.jpg",
  "created_at": "2026-01-07T10:00:00",
  "updated_at": "2026-01-07T10:00:00"
}
```

### Image Analysis

#### Create Image Analysis

```http
POST /api/v1/image-analysis/{image_id}/analyze
X-API-Key: your-api-key

Response: 201 Created
{
  "id": "analysis-uuid",
  "image_id": "image-uuid",
  "skin_type": "Oily",
  "issues": ["Acne", "Redness"],
  "confidence_score": 0.92,
  "model_version": "v1.0.0-mock",
  "created_at": "2026-01-07T10:00:00",
  "updated_at": "2026-01-07T10:00:00"
}
```

**Requirements:**

- Valid API key with `analyze` scope
- Image must exist in the system

**Skin Types:** `Oily`, `Dry`, `Combination`, `Normal`  
**Skin Issues:** `Acne`, `Hyperpigmentation`, `Wrinkles`, `Redness`

#### Get Latest Analysis

```http
GET /api/v1/image-analysis/{image_id}/analysis
X-API-Key: your-api-key

Response: 200 OK
{
  "id": "analysis-uuid",
  "image_id": "image-uuid",
  "skin_type": "Oily",
  "issues": ["Acne", "Redness"],
  "confidence_score": 0.92,
  "model_version": "v1.0.0-mock",
  "created_at": "2026-01-07T10:00:00",
  "updated_at": "2026-01-07T10:00:00"
}
```

### Health & Status

#### Health Check

```http
GET /health

Response: 200 OK
{
  "status": "healthy",
  "database": "connected",
  "service": "Veefyed API"
}
```

#### Root Endpoint

```http
GET /

Response: 200 OK
{
  "message": "Veefyed API is running!",
  "status": "success",
  "docs": "Visit /docs to view API documentation"
}
```

## Project Structure

```
veefyed/
├── src/
│   ├── api/
│   │   ├── routes/           # API endpoints
│   │   │   ├── image.py      # Image upload/retrieval
│   │   │   ├── image_analysis.py  # Analysis endpoints
│   │   │   └── api_key.py    # API key management
│   │   ├── dependencies/     # FastAPI dependencies
│   │   ├── middleware.py     # CORS, logging, etc.
│   │   └── main.py          # FastAPI app initialization
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   ├── logger_config.py # Logging setup
│   │   └── tasks.py         # Startup/shutdown tasks
│   ├── db/
│   │   ├── repositories/    # Database operations
│   │   └── migrations/      # Alembic migrations
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   │   ├── image_analysis_service.py
│   │   └── third_party/     # External services
│   ├── utils/               # Helper functions
│   ├── enums/               # Enum definitions
│   └── errors/              # Custom exceptions
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── docker-compose.yml
├── Dockerfile.dev
├── alembic.ini
├── requirements.txt
└── README.md
```

## Testing

The project includes comprehensive test coverage:

- **Unit Tests**: Models, helpers, services, repositories
- **Integration Tests**: API endpoints
- **Test Coverage**: ~60% overall

See [README_TESTS.md](README_TESTS.md) for detailed testing documentation.

## Assumptions Made

### Authentication & Security

1. **API Key Storage**: API keys are hashed using Argon2 (not reversible)
2. **Scope-Based Access**: API keys have specific scopes (`upload`, `analyze`)
3. **No User Management**: API keys are created directly without user accounts
4. **Single Tenant**: No multi-tenancy or organization separation

### Image Processing

1. **Local Storage**: Images stored on local filesystem (not cloud storage)
2. **No Image Serving**: API only stores metadata; actual image retrieval not implemented
3. **File Formats**: Only JPEG and PNG supported
4. **Size Limit**: 5MB maximum per image
5. **No Image Preprocessing**: Images stored as-is without optimization

### AI/ML Analysis

1. **Mock Implementation**: Current analysis generates random mock data
2. **No Real Model**: Placeholder for actual AI/ML integration
3. **Single Analysis**: Only latest analysis stored per image
4. **Confidence Score**: Range 0.75-0.98 (mocked)

### Database

1. **SQLite for Development**: Production should use PostgreSQL
2. **Soft Deletes**: Records marked as deleted, not physically removed
3. **No Pagination**: Endpoints don't implement pagination yet
4. **No Search/Filtering**: Limited query capabilities

### Infrastructure

1. **Redis for Sessions**: Not fully utilized in current implementation
2. **No Rate Limiting**: API calls not rate-limited
3. **No Monitoring**: No APM or metrics collection
4. **Development Config**: CORS allows all origins

## Production Improvements

### Security & Authentication

- [ ] **OAuth2/JWT Authentication**: Replace API keys with OAuth2 flow
- [ ] **API Key Rotation**: Implement key rotation and expiration
- [ ] **Rate Limiting**: Add per-key rate limits using Redis
- [ ] **Input Sanitization**: Enhanced validation and sanitization
- [ ] **HTTPS Only**: Enforce TLS/SSL in production
- [ ] **Secrets Management**: Use vault (AWS Secrets Manager, HashiCorp Vault)
- [ ] **CORS Configuration**: Restrict to specific domains
- [ ] **API Versioning**: Proper versioning strategy

### Image Storage & Processing

- [ ] **Cloud Storage**: Migrate to S3/GCS/Azure Blob Storage
- [ ] **CDN Integration**: Serve images through CDN (CloudFront, CloudFlare)
- [ ] **Image Optimization**: Compress/resize on upload
- [ ] **Multiple Formats**: Support WebP, AVIF
- [ ] **Virus Scanning**: Scan uploads for malware
- [ ] **Thumbnail Generation**: Auto-generate thumbnails
- [ ] **Signed URLs**: Time-limited access to images
- [ ] **Image Deletion**: Implement physical file cleanup

### AI/ML Integration

- [ ] **Real Model Integration**: Replace mock with actual AI model
- [ ] **Model Versioning**: Track and manage model versions
- [ ] **Async Processing**: Queue-based analysis (Celery/RQ)
- [ ] **Model Monitoring**: Track accuracy, drift, performance
- [ ] **A/B Testing**: Compare model versions
- [ ] **Confidence Thresholds**: Flag low-confidence results
- [ ] **Multi-Model Support**: Ensemble predictions

### Database & Performance

- [ ] **PostgreSQL**: Migrate from SQLite
- [ ] **Connection Pooling**: Optimize database connections
- [ ] **Database Indexing**: Add indexes for common queries
- [ ] **Pagination**: Implement cursor-based pagination
- [ ] **Caching**: Redis caching for frequent queries
- [ ] **Read Replicas**: Separate read/write databases
- [ ] **Query Optimization**: Analyze and optimize slow queries
- [ ] **Archival Strategy**: Move old data to cold storage

### Observability & Monitoring

- [ ] **Logging**: Structured logging (JSON format)
- [ ] **APM**: Application Performance Monitoring (DataDog, New Relic)
- [ ] **Metrics**: Prometheus/Grafana for metrics
- [ ] **Distributed Tracing**: OpenTelemetry integration
- [ ] **Error Tracking**: Sentry for error monitoring
- [ ] **Health Checks**: Enhanced health endpoints
- [ ] **Alerting**: PagerDuty/OpsGenie integration

### API Improvements

- [ ] **GraphQL**: Consider GraphQL for flexible querying
- [ ] **Webhooks**: Event notifications for analysis completion
- [ ] **Batch Operations**: Bulk upload/analysis
- [ ] **Filtering & Search**: Advanced query capabilities
- [ ] **API Documentation**: OpenAPI spec enhancements
- [ ] **Response Compression**: Gzip compression
- [ ] **Request Validation**: Enhanced input validation

### Infrastructure & DevOps

- [ ] **Kubernetes**: Container orchestration
- [ ] **Auto-Scaling**: Horizontal pod autoscaling
- [ ] **CI/CD**: GitHub Actions/GitLab CI
- [ ] **Infrastructure as Code**: Terraform/CloudFormation
- [ ] **Blue-Green Deployments**: Zero-downtime deployments
- [ ] **Backup Strategy**: Automated database backups
- [ ] **Disaster Recovery**: Multi-region deployment
- [ ] **Load Balancing**: Application load balancers

### Testing & Quality

- [ ] **Integration Tests**: Full API integration tests
- [ ] **Load Testing**: Performance benchmarking (Locust, k6)
- [ ] **Security Testing**: OWASP compliance, penetration testing
- [ ] **Contract Testing**: API contract validation
- [ ] **E2E Tests**: End-to-end user flows
- [ ] **Code Coverage**: Target 80%+ coverage
- [ ] **Static Analysis**: SonarQube integration

### Compliance & Legal

- [ ] **GDPR Compliance**: Data privacy regulations
- [ ] **Data Retention**: Configurable retention policies
- [ ] **Audit Logging**: Track all data access
- [ ] **Terms of Service**: API usage terms
- [ ] **Privacy Policy**: Data handling transparency
- [ ] **Medical Compliance**: HIPAA if handling health data

### User Experience

- [ ] **Client SDKs**: Python, JavaScript, Go SDKs
- [ ] **Postman Collection**: Pre-configured API collection
- [ ] **Interactive Playground**: API testing interface
- [ ] **Status Page**: Public API status (StatusPage.io)
- [ ] **Documentation**: Detailed guides and tutorials
- [ ] **Changelog**: Version history and breaking changes

## License

[Specify your license here]

## Contact

For questions or support, contact: [your-email@example.com]
