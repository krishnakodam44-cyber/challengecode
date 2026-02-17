# Metadata Service

A FastAPI-based metadata service for dataset lineage tracking and management.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed

### Run the Application

```bash
docker compose up
```

This will start:
- **API Server**: http://localhost:8000
- **MySQL Database**: localhost:3307

### Access the API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## Architecture Decisions

### Technology Stack
- **FastAPI**: Modern, fast Python web framework with automatic API documentation and built-in validation
- **SQLAlchemy**: ORM for database abstraction and type-safe queries
- **MySQL**: Reliable relational database for structured metadata storage
- **Pydantic**: Data validation and serialization with automatic OpenAPI schema generation

### Design Principles

1. **Containerization**: Docker and Docker Compose for environment consistency and reproducible deployments
2. **Separation of Concerns**: 
   - `models/` - Database models and SQLAlchemy ORM definitions
   - `schemas/` - Pydantic data validation schemas
   - `db/` - Database connection and session management
   - `core/` - Application configuration
3. **Hot Reload**: Development mode with auto-reload for rapid iteration
4. **Connection Pooling**: SQLAlchemy session management for efficient database handling
5. **Environment Configuration**: `.env` file for sensitive data and environment-specific settings

### Key Design Features

- **Automatic API Documentation**: FastAPI generates OpenAPI/Swagger docs automatically
- **Type Safety**: Pydantic models ensure runtime validation and type hints
- **Database Abstraction**: SQLAlchemy ORM allows flexible database queries
- **Layered Architecture**: Clean separation between API layer, business logic, and data persistence

## Development

### Local Setup (with Python)

```bash
# Install dependencies
poetry install

# Run the application
uvicorn main:app --reload
```

### Environment Variables

See `.env` file for configuration:
- `DATABASE_URL`: MySQL connection string
- `MYSQL_USER`: Database user
- `MYSQL_PASSWORD`: Database password
- `MYSQL_DATABASE`: Database name

## Project Structure

```
├── main.py                 # FastAPI application entry point
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── pyproject.toml          # Poetry dependencies
├── .env                    # Environment configuration
├── core/
│   └── config.py          # Application settings
├── models/
│   ├── base.py            # SQLAlchemy base class
│   ├── metadata.py        # Database models
│   └── __init__.py
├── schemas/
│   ├── metadata.py        # Pydantic schemas
│   └── __init__.py
├── db/
│   └── session.py         # Database session management
└── tests/                 # Test suite
```

## API Endpoints

All API endpoints are documented in the Swagger UI at `/docs` when the application is running.

- `GET /` - Health check endpoint