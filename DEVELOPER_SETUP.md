# TransitOps — Developer Setup & Local Execution Guide

## Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- PostgreSQL 15+ running on `localhost:5432`

---

## 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create & activate virtual environment (optional)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy .env.example to .env and configure DATABASE_URL:
# DATABASE_URL=postgresql+psycopg2://postgres:1234@localhost:5432/transitops

# Run database migrations
alembic upgrade head

# Start backend dev server
uvicorn app.main:app --reload --port 8000
```

FastAPI Interactive Swagger Docs available at: `http://localhost:8000/docs`

---

## 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Application UI available at: `http://localhost:5173`

---

## 3. Running Test Suites

```bash
# Run backend pytest suite
cd backend
python -m pytest -v

# Run frontend build check
cd frontend
npm run build

# Run Playwright End-to-End specs
cd frontend
npx playwright test
```
