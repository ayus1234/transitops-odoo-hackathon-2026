# TransitOps Backend API

FastAPI backend for TransitOps - Smart Transport Operations Platform.

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   │   ├── deps.py       # Dependencies (auth, db session)
│   │   └── v1/           # API version 1
│   │       ├── auth.py   # Authentication endpoints
│   │       └── ...       # Other endpoint modules
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings and environment variables
│   │   ├── database.py   # Database connection
│   │   └── security.py   # JWT and password hashing
│   ├── models/           # SQLAlchemy models
│   │   ├── user.py
│   │   ├── role.py
│   │   └── ...
│   ├── schemas/          # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── common.py
│   │   └── ...
│   ├── services/         # Business logic layer
│   ├── repositories/     # Database operations layer
│   ├── utils/            # Utility functions
│   │   └── exceptions.py # Custom exceptions
│   └── main.py           # FastAPI application entry point
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py            # Alembic environment
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment variables
└── README.md             # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip or uv

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` file from example:

```bash
copy .env.example .env
```

Update the following variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/transitops

# JWT Security (IMPORTANT: Change this!)
SECRET_KEY=generate-a-secure-random-key-here-at-least-32-characters-long

# CORS (Update for your frontend URL)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### 5. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE transitops;

# Exit
\q
```

### 6. Run Database Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 7. Seed Initial Data

Create a seed script to add roles and admin user (see seed_data.py below).

```bash
python seed_data.py
```

### 8. Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py directly
python app/main.py
```

### 9. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - Logout (client-side token removal)

### Future Endpoints (To be implemented)

- Vehicles: `/api/v1/vehicles`
- Drivers: `/api/v1/drivers`
- Trips: `/api/v1/trips`
- Maintenance: `/api/v1/maintenance`
- Fuel Logs: `/api/v1/fuel-logs`
- Expenses: `/api/v1/expenses`
- Reports: `/api/v1/reports`
- Dashboard: `/api/v1/dashboard`

## Authentication

All endpoints (except `/auth/login`) require JWT authentication.

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@transitops.com",
    "password": "admin123"
  }'
```

### Use Token

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Database Migrations

### Create New Migration

```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### View Migration History

```bash
alembic history
```

## Development

### Code Structure

The application follows a layered architecture:

1. **API Layer** (`app/api/`) - HTTP endpoints, request/response handling
2. **Service Layer** (`app/services/`) - Business logic
3. **Repository Layer** (`app/repositories/`) - Database operations
4. **Model Layer** (`app/models/`) - SQLAlchemy ORM models
5. **Schema Layer** (`app/schemas/`) - Pydantic validation schemas

### Adding New Endpoint

1. Create model in `app/models/`
2. Create schemas in `app/schemas/`
3. Create repository in `app/repositories/`
4. Create service in `app/services/`
5. Create API route in `app/api/v1/`
6. Register route in `app/api/v1/__init__.py`

### RBAC (Role-Based Access Control)

Use the `RoleChecker` or `PermissionChecker` dependencies:

```python
from app.api.deps import RoleChecker

@router.get("/admin-only", dependencies=[Depends(RoleChecker(["Fleet Manager"]))])
def admin_route():
    return {"message": "Admin access granted"}
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Set `ENVIRONMENT=production` in `.env`
3. Use a strong `SECRET_KEY`
4. Use environment-specific database
5. Configure proper CORS origins
6. Use a production WSGI server (Gunicorn + Uvicorn)

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key (min 32 chars) | Required |
| `DEBUG` | Debug mode | `False` |
| `ENVIRONMENT` | Environment (development/production) | `development` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `60` |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000"]` |

## Common Issues

### Database Connection Error

- Check PostgreSQL is running
- Verify DATABASE_URL is correct
- Ensure database exists

### Import Errors

- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### Migration Errors

- Check database is accessible
- Verify all models are imported in `alembic/env.py`
- Try `alembic downgrade -1` then `alembic upgrade head`

## Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Run tests
5. Submit pull request

## License

Proprietary - TransitOps Platform
