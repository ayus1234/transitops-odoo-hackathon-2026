# TransitOps Backend - Quick Start Guide

This guide will help you get the backend up and running in under 5 minutes.

## Prerequisites

✅ Python 3.11+  
✅ PostgreSQL 15+  
✅ Git  

---

## Setup (Windows)

### Step 1: Create Database

```cmd
psql -U postgres
CREATE DATABASE transitops;
\q
```

### Step 2: Setup Backend

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure Environment

```cmd
copy .env.example .env
```

Edit `.env` and update:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/transitops
SECRET_KEY=generate-a-secure-random-32-character-key-here
```

### Step 4: Run Migrations

```cmd
alembic upgrade head
```

### Step 5: Seed Initial Data

```cmd
python seed_data.py
```

### Step 6: Start Server

```cmd
uvicorn app.main:app --reload
```

---

## Setup (Linux/Mac)

### Step 1: Create Database

```bash
psql -U postgres
CREATE DATABASE transitops;
\q
```

### Step 2: Setup Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and update:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/transitops
SECRET_KEY=generate-a-secure-random-32-character-key-here
```

### Step 4: Run Migrations

```bash
alembic upgrade head
```

### Step 5: Seed Initial Data

```bash
python seed_data.py
```

### Step 6: Start Server

```bash
uvicorn app.main:app --reload
```

---

## Verify Installation

Open your browser and visit:

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Test Authentication

### Using Swagger UI (http://localhost:8000/docs)

1. Click on `POST /api/v1/auth/login`
2. Click "Try it out"
3. Enter credentials:
   ```json
   {
     "email": "admin@transitops.com",
     "password": "admin123"
   }
   ```
4. Click "Execute"
5. Copy the `access_token` from the response
6. Click "Authorize" button (top right)
7. Enter: `Bearer YOUR_TOKEN`
8. Test other endpoints!

### Using cURL

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@transitops.com",
    "password": "admin123"
  }'

# Get current user (replace TOKEN with the token from login)
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer TOKEN"
```

---

## Default Credentials

After seeding, you can login with these accounts:

### Admin (Fleet Manager)
- **Email**: admin@transitops.com
- **Password**: admin123

### Driver
- **Email**: driver@transitops.com
- **Password**: driver123

### Safety Officer
- **Email**: safety@transitops.com
- **Password**: safety123

### Financial Analyst
- **Email**: finance@transitops.com
- **Password**: finance123

---

## Common Commands

### Start Development Server
```bash
uvicorn app.main:app --reload
```

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

### Run Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=app tests/
```

---

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Config, database, security
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic (to be implemented)
│   ├── repositories/    # Database operations (to be implemented)
│   └── main.py          # FastAPI app
├── alembic/             # Database migrations
├── tests/               # Test files
└── seed_data.py         # Initial data seeding
```

---

## Next Steps

Now that the foundation is ready, you can:

1. ✅ **Implement Business Modules** (Vehicles, Drivers, Trips, etc.)
2. ✅ **Add Business Logic** in services layer
3. ✅ **Create API Endpoints** for each module
4. ✅ **Connect Frontend** to backend APIs
5. ✅ **Write Tests** for each module

---

## Troubleshooting

### Database Connection Error
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Solution**: 
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure database exists

### Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**:
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check you're in the `backend/` directory

### Migration Errors
```
alembic.util.exc.CommandError
```
**Solution**:
- Check database connection
- Verify alembic.ini configuration
- Try `alembic downgrade -1` then `alembic upgrade head`

### Port Already in Use
```
ERROR: Address already in use
```
**Solution**:
- Kill existing process on port 8000
- Or use different port: `uvicorn app.main:app --reload --port 8001`

---

## Support

For issues and questions:
1. Check the main [README.md](README.md)
2. Review [DATABASE_SCHEMA.md](../DATABASE_SCHEMA.md)
3. Review [API_SPECIFICATION.md](../API_SPECIFICATION.md)

---

## Ready? Let's Build! 🚀

The foundation is complete. Now you can start implementing business modules following the architecture defined in PROJECT_STRUCTURE.md.
