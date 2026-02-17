# Metadata Service

A FastAPI-based metadata service for dataset lineage tracking and management.

## Dependencies

### System Requirements
- **Docker**: v20.10+
- **Docker Compose**: v2.0+
- **Python**: 3.11+ (for local development without Docker)

### Python Dependencies (installed automatically)
- `fastapi==0.111.0` - Web framework
- `uvicorn[standard]==0.30.0` - ASGI server
- `sqlalchemy==2.0.30` - ORM and database toolkit
- `pymysql==1.1.1` - MySQL database driver
- `pydantic-settings==2.3.4` - Settings management
- `python-dotenv==1.0.1` - Environment variable loading

See `pyproject.toml` for complete dependency list.

## Quick Start

### Option 1: Run with Docker Compose (Recommended)

#### Prerequisites
- Docker and Docker Compose installed

#### Commands

```bash
# Clone the repository
git clone https://github.com/krishnakodam44-cyber/challengecode.git
cd challengecode/app

# Start the application and database
docker compose up

# In another terminal, stop the application
docker compose down

# View logs
docker compose logs -f api
```

This will start:
- **API Server**: http://localhost:8000
- **MySQL Database**: localhost:3307

### Option 2: Run Locally (with Python)

#### Prerequisites
- Python 3.11+
- Poetry package manager

#### Commands

```bash
# Clone the repository
git clone https://github.com/krishnakodam44-cyber/challengecode.git
cd challengecode/app

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Create database tables (ensure MySQL is running)
# Modify DATABASE_URL in .env to point to your MySQL instance

# Run the application
uvicorn main:app --reload

# Deactivate environment
exit
```

### Access the API

- **Swagger UI (Interactive Docs)**: http://localhost:8000/docs
- **ReDoc (Alternative Docs)**: http://localhost:8000/redoc
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

### Local Setup Commands

#### Install Dependencies
```bash
# Using Poetry
poetry install

# Activate virtual environment
poetry shell
```

#### Run the Application Locally
```bash
# Start development server with auto-reload
uvicorn main:app --reload

# Run on specific host and port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Database Management
```bash
# Connect to MySQL locally
mysql -h localhost -P 3307 -u metadata -p metadata_db

# Connection string for .env
DATABASE_URL=mysql+pymysql://metadata:metadata@localhost:3307/metadata_db
```

#### Code Quality Tools
```bash
# Format code with Black
poetry run black .

# Sort imports with isort
poetry run isort .

# Lint with flake8
poetry run flake8 .

# Run all checks
poetry run black . && poetry run isort . && poetry run flake8 .
```

### Environment Variables

See `.env` file for configuration:
- `DATABASE_URL`: MySQL connection string
- `MYSQL_USER`: Database user
- `MYSQL_PASSWORD`: Database password
- `MYSQL_DATABASE`: Database name

### Docker Commands

```bash
# Build Docker image
docker build -t metadata-service .

# Start services in background
docker compose up -d

# View running containers
docker compose ps

# View application logs
docker compose logs -f api

# Stop all services
docker compose down

# Remove all volumes (WARNING: deletes data)
docker compose down -v

# Rebuild containers
docker compose up --build
```

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

All API endpoints are automatically documented in the interactive Swagger UI at `/docs` when the application is running.

### Available Endpoints

- **`GET /`** - Health check endpoint
  - Returns: `{"status": "ok"}`

- **`POST /datasets`** - Create a new dataset
  - Request body: Dataset metadata
  
- **`GET /datasets`** - List all datasets

- **`GET /datasets/{fqn}`** - Get dataset by fully-qualified name

- **`POST /lineage`** - Add lineage relationship between datasets

- **`GET /lineage/{fqn}`** - Get lineage information for a dataset

- **`GET /search`** - Search datasets by query

### API Documentation UI

The application includes interactive API documentation:

**Swagger UI (default)**: http://localhost:8000/docs
- Full API exploration and testing interface
- Try out endpoints directly from the browser
- Request/response examples

**ReDoc (alternative)**: http://localhost:8000/redoc
- Clean, read-only API documentation
- Organized by tags and resources

### Sample Response

```json
{
  "status": "ok"
}
```

### Usage Example

Once the application is running, you can test endpoints:

```bash
# Health check
curl http://localhost:8000/

# Create a dataset
curl -X POST http://localhost:8000/datasets \
  -H "Content-Type: application/json" \
  -d '{
    "fqn": "production.warehouse.customers",
    "name": "Customers Table",
    "owner": "data-team"
  }'

# Get all datasets
curl http://localhost:8000/datasets

# Search datasets
curl "http://localhost:8000/search?query=customers"
```