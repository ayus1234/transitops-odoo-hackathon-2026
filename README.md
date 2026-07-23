# TransitOps Enterprise ERP

![TransitOps Banner](https://img.shields.io/badge/TransitOps-Enterprise%20ERP-blue?style=for-the-badge) ![Version](https://img.shields.io/badge/version-1.0.0-green?style=for-the-badge) ![Build](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge)

TransitOps is a comprehensive, enterprise-grade Enterprise Resource Planning (ERP) platform designed specifically for modern fleet, transport, and logistics management. 

Built from the ground up for scalability, responsiveness, and performance, TransitOps handles everything from vehicle telemetry and driver assignments to procurement and real-time operational analytics.

---

## 🌟 Key Features & Modules

### 1. 🚛 Fleet Management
* **Vehicle Registry:** Complete CRUD operations for vehicles, including registration numbers, capacity, models, status, and compliance.
* **Driver Management:** Track driver licenses, active statuses, assignments, and safety insights.
* **Fleet Compliance:** Track expiring licenses, registrations, and regulatory requirements proactively.

### 2. 🗺️ Trip & Dispatch Operations
* **Trip Execution:** Schedule trips, assign drivers and vehicles, and track real-time progression (Scheduled ➡️ In Progress ➡️ Completed).
* **Granular Real-Time Tracking:** Fleet Map integration (Google Maps API) to visualize vehicle locations and trip statuses dynamically.

### 3. 🛠️ Maintenance Operations
* **Maintenance Scheduler:** Preventive and reactive maintenance job scheduling.
* **Work Order Details:** Detailed breakdowns of tasks, assigned technicians, and resolution notes.
* **Technician Workload Management:** Track technician availability and active assignments.

### 4. 📦 Inventory & Procurement
* **Inventory Management:** Multi-tiered tracking of spare parts and assets. Auto-stock-level alerts prevent shortages.
* **Purchase Orders (POs):** End-to-end procurement workflow (Draft ➡️ Approved ➡️ Ordered ➡️ Delivered).
* **Vendor Portal Integration:** Track suppliers and procurement expenditures.

### 5. 📊 Reporting, Analytics, & Financials
* **Dynamic Dashboard:** Real-time KPIs covering trips, maintenance costs, fuel expenses, and fleet profitability.
* **Custom Report Builder:** Generate tailored reports with powerful filters.
* **Export Engine:** Standardized CSV and PDF data exports for compliance and off-platform analysis.
* **Fuel & Expenses:** Track fuel consumption, operational expenses, and calculate overall fleet profitability.

### 6. 🔐 Security & Administration
* **Role-Based Access Control (RBAC):** Granular permission system securing both API endpoints and UI views. Define custom roles (Admin, Dispatcher, Technician, Driver).
* **Global Admin Settings:** Centralized configuration for company details, preferences, and system behavior.
* **Audit Logs & Activity Feeds:** Track system-wide events and data mutations securely.

### 7. 📱 Modern User Experience
* **Responsive Interface:** Fluid design tailored for mobile operators (320px) up to ultra-wide command centers (3840px).
* **Quick Actions:** Globally accessible shortcuts for rapid data entry (e.g., "New Trip", "Log Maintenance").
* **Dark Mode & Theming:** Integrated context-driven theme support.

---

## 🏗️ Architecture & Technology Stack

**Backend (Python/FastAPI):**
- **Framework:** FastAPI (High performance, async/await support).
- **ORM & Database:** SQLAlchemy (Unit of Work pattern) backed by **PostgreSQL 15+**.
- **Migrations:** Alembic.
- **Architecture:** Layered architecture (Routers ➡️ Services ➡️ Repositories ➡️ Models) ensuring clean separation of concerns.

**Frontend (React/Vite):**
- **Framework:** React 18+ powered by Vite.
- **State Management:** React Context API (Auth, UI, Theme, Toast, Offline capabilities).
- **Styling:** Tailwind CSS integrated with Vanilla CSS for high-performance rendering.
- **Maps:** Google Maps integration.

---

## 🗂️ Project Structure

The repository is organized into two main monolithic components:

```text
transitops-odoo-hackathon-2026/
├── backend/                  # FastAPI Application
│   ├── alembic/              # Database migration scripts
│   ├── app/                  
│   │   ├── api/              # API Routers & Endpoints (v1)
│   │   ├── core/             # Configuration & Security (JWT, Config)
│   │   ├── models/           # SQLAlchemy ORM Models
│   │   ├── repositories/     # Database access layer (Unit of Work)
│   │   ├── schemas/          # Pydantic schemas (Validation)
│   │   └── services/         # Business Logic Layer
│   ├── scripts/              # Seed scripts, data generation
│   └── tests/                # Pytest suites
└── frontend/                 # React + Vite Application
    ├── public/               # Static assets
    ├── src/
    │   ├── assets/           # Images, Fonts, Global CSS
    │   ├── components/       # Reusable UI components (Layout, UI, Forms)
    │   ├── context/          # React Context (Auth, Theme)
    │   ├── hooks/            # Custom React Hooks
    │   ├── pages/            # Page-level components (Dashboard, Fleet, Trips)
    │   ├── services/         # Axios API clients
    │   └── utils/            # Helper functions
    └── tests/                # Playwright E2E Tests
```

---

## ⚙️ Architecture Workflow

TransitOps utilizes a highly scalable layered architecture design for both the frontend and backend.

### Backend Request Lifecycle
1. **Router (`api/v1/`):** Receives HTTP request, handles JWT authorization (RBAC), and validates payload using Pydantic schemas.
2. **Service (`services/`):** Executes complex business logic (e.g., verifying driver availability, transitioning vehicle states).
3. **Repository (`repositories/`):** Interacts securely with PostgreSQL via SQLAlchemy ORM, ensuring ACID transaction compliance.
4. **Database:** PostgreSQL executes the query and returns data through the layers back to the client.

### Frontend Component Lifecycle
1. **Page/View (`pages/`):** React component mounts and uses `useEffect` to trigger a data fetch via custom hooks.
2. **API Client (`services/`):** Axios sends an authenticated HTTP request to the FastAPI backend.
3. **Context (`context/`):** Global states (like user permissions, toasts, and themes) dynamically update the UI based on the API response.
4. **Rendering:** UI components render data using TailwindCSS and custom utility classes.

---

## 🧪 Testing & Performance Validation

TransitOps is rigorously tested for enterprise deployments:
- **Backend Regression Tests:** 233/233 Pytest cases passing (100% coverage on core services).
- **Frontend E2E Tests:** 15/15 Playwright E2E tests passing, covering cross-module workflows.
- **Enterprise Dataset Benchmarking:** Application validated against a massive synthetic dataset (10,000+ logs, 2,000+ trips). The dataset is fully localized for the Indian context, featuring authentic Indian commercial vehicle models, regional registration number formats, and nationwide trip routing between major Indian cities.
- **API Performance:** Sub-100ms P95 latency on paginated, heavily indexed queries.
- **Database:** Full migration to PostgreSQL verified with ACID compliance.

---

## 📖 Documentation Directory
For deep technical dives into the platform, consult the following documentation artifacts:
- `PROJECT_STRUCTURE.md` - Complete repository layout and module boundaries.
- `API_SPECIFICATION.md` - Exhaustive backend REST API routes and schemas.
- `DATABASE_SCHEMA.md` - PostgreSQL Entity-Relationship modeling and schema descriptions.
- `PRODUCTION_READINESS.md` - Audit of application readiness, performance metrics, and QA sign-offs.
- `DEPLOYMENT.md` - Guide to deploying in production environments (Nginx, PM2, Gunicorn).
- `CHANGELOG.md` - Release history for v1.0.0.

---

## 🚀 Quick Start (Development)

**1. Clone the repository and setup the database:**
Ensure PostgreSQL is running and create a database named `transitops`. Update your `.env` file accordingly.

**2. Run the Backend:**
```bash
cd backend
python -m venv .venv
# Activate the virtual environment
# Windows: .venv\Scripts\activate | Unix: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload
```

**3. Run the Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to access the TransitOps application.
