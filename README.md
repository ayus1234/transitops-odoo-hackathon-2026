# TransitOps Enterprise ERP

TransitOps is a comprehensive, enterprise-grade Enterprise Resource Planning (ERP) platform designed specifically for modern fleet and transit management.

## Key Features
- **Fleet Management:** Vehicle registration, assignments, odometer tracking, and compliance.
- **Trip & Dispatch:** Advanced trip routing, dispatch operations, and real-time status.
- **Maintenance Operations:** Preventive and reactive maintenance job scheduling.
- **Inventory & Procurement:** Multi-tiered inventory, auto-stock-level alerts, and end-to-end Purchase Order workflow.
- **Reporting & Analytics:** Real-time KPIs, highly configurable tabular reporting, and CSV/PDF data exports.
- **Role-Based Access Control:** Granular permission system securing endpoints and UI views.
- **Responsive Interface:** Fluid design tailored for mobile operators up to ultra-wide command centers.

## Architecture
- **Backend:** FastAPI, Python 3.10+, SQLAlchemy (Async/Sync UOW), PostgreSQL 15+.
- **Frontend:** React 18+, Vite, Context API, Tailwind/Vanilla CSS integrations.
- **Testing:** Pytest (Backend, 230+ tests), Playwright (Frontend E2E).

## Testing Summary
- 233 Backend Regression Tests Passed
- 15/15 Playwright E2E Tests Passed
- PostgreSQL Migration Verified
- Enterprise Dataset Performance Benchmarked (10k+ records, sub-100ms API responses)
- Cross-Module Integration Testing Completed
- Responsive Testing Completed (320px–3840px)
- Production Build Verification Completed
- Performance & Stability Testing Completed

## Documentation
- `PROJECT_STRUCTURE.md` - Repository layout.
- `API_SPECIFICATION.md` - Backend REST API routes and schemas.
- `DATABASE_SCHEMA.md` - PostgreSQL ERD and schema descriptions.
- `PRODUCTION_READINESS.md` - Audit of application readiness and performance.
- `DEPLOYMENT.md` - Guide to deploying in production environments.
- `CHANGELOG.md` - Release history.

## Quick Start (Development)
**Backend:**
```bash
cd backend
python -m venv venv
# activate venv
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## License
Proprietary / Internal - Not for open-source distribution without authorization.
