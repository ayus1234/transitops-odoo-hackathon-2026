# TransitOps Enterprise ERP

![TransitOps Banner](https://img.shields.io/badge/TransitOps-Enterprise%20ERP-blue?style=for-the-badge) ![Version](https://img.shields.io/badge/version-1.1.0-green?style=for-the-badge) ![Build](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge) ![RBAC](https://img.shields.io/badge/RBAC-13%20Enterprise%20Roles-indigo?style=for-the-badge)

**TransitOps** is a comprehensive, AI-enhanced, enterprise-grade Enterprise Resource Planning (ERP) platform designed specifically for modern fleet, transport, logistics, maintenance, and procurement management. 

Built from the ground up for scalability, responsiveness, strict type safety, and real-time operational execution, TransitOps seamlessly handles everything from vehicle telemetry and driver assignments to multi-tier procurement workflows, automated inventory alerts, and role-governed security analytics.

---

## 🌟 Key Features & Modules

### 1. 🔐 Enterprise 13-Role Zero-Trust RBAC & Security Governance
* **Comprehensive 13-Role Matrix:** Granular Role-Based Access Control adhering strictly to the Principle of Least Privilege (PoLP) without arbitrary hardcoded resource bypasses across all API routes and UI viewports for:
  - **Executive & Governance:** *Super Admin*, *Administrator*, *System Admin*
  - **Operations & Logistics:** *Fleet Manager*, *Dispatcher*, *Driver*, *HR/Operations*
  - **Maintenance & Asset Engineering:** *Maintenance Manager*, *Technician*, *Safety Officer*
  - **Finance, Procurement & Support:** *Financial Analyst*, *Procurement Operations*, *Support Agent*
* **Dynamic RBAC Audit Engine:** Automated recording of authentic permission mutations, role assignments, custom role creations, and administrative events in persistent database audit logs with export capability.
* **Self-Healing Startup Synchronization:** Automatically verifies and synchronizes all 13 canonical enterprise roles and default capability matrices without overriding user-defined custom roles or altering credential hashes during runtime login.

### 2. 🚛 Fleet & Driver Operations
* **Vehicle Registry:** Complete lifecycle management and CRUD operations for transport assets, including registration numbers, volumetric capacities, telemetry models, and real-time compliance tracking.
* **Driver Management & Safety Insights:** Track driver licensing, dynamic active statuses, assignments, and calculate AI-driven safety scores and compliance expirations.

### 3. 🗺️ Trip Execution & Real-Time Telemetry
* **Trip Execution & Dispatching:** End-to-end trip creation, scheduling, driver/vehicle pairing, and real-time status progression (*Scheduled* ➡️ *Dispatched* / *In Progress* ➡️ *Completed*).
* **Full Fleet Mapping:** Integrated interactive map visualization displaying dynamic vehicle coordinates, operational boundaries, and active trip paths.

### 4. 🛠️ Preventive Maintenance & Workshop Command
* **Maintenance Scheduler:** Automated preventive maintenance scheduling and reactive repair job ticketing.
* **Work Order & Task Tracking:** Granular task breakdown, technician assignments, repair notes, and inspection completion checklists.

### 5. 📦 Supply Chain: Inventory & Procurement
* **Multi-Tier Inventory Tracking:** Real-time stock alerts, minimum reorder thresholds, and automated reorder triggers for workshop spare parts and fleet assets.
* **End-to-End Purchase Orders (POs):** Complete procurement lifecycle governance (*Draft* ➡️ *Pending Approval* ➡️ *Approved* ➡️ *Ordered* ➡️ *Delivered*) with vendor relationship oversight.

### 6. 📊 Dynamic Reporting, Analytics, & Financials
* **Real-Time Command Dashboard:** Dynamic KPI aggregations covering live trips, maintenance expenditure, fuel efficiency, operational costs, and fleet net profitability.
* **Custom Report Builder & Export Engine:** Advanced filtering with standardized PDF and CSV document generation for offline auditing and compliance.
* **Fuel & Financial Analytics:** Comprehensive fuel consumption tracking and departmental cost categorization.

### 7. 📱 Premium UI/UX & Interactive Showcase
* **Evaluator-Friendly Login Showcase:** Clicking deployed links automatically routes to a pristine interactive login interface (`/login`), resetting prior session caches and enabling one-click seamless persona switching between all 13 enterprise roles without credential conflicts.
* **Standardized Interactive Modals:** Ergonomic, unified user confirmation dialogs across all operational mutations and system sign-out actions.
* **Responsive Command Viewport:** Optimized fluid typography and table spacing guaranteed against layout truncation from mobile operators (320px) up to ultra-wide desktop command centers (3840px).

---

## 🏗️ Architecture & Technology Stack

### **Backend (Python / FastAPI / SQLAlchemy):**
- **Framework:** FastAPI (Asynchronous high-performance execution with OpenAPI automation).
- **ORM & Data Persistence:** SQLAlchemy 2.0+ (Unit of Work and Repository design patterns) backed by **PostgreSQL 15+** (compatible with SQLite for local execution).
- **Security & Validation:** Strict type-safe Pydantic schema validation, JWT bearer token authorization, and automated timezone-aware UTC timestamps (`datetime.now(timezone.utc)`).
- **Serverless & Edge Deployment:** Serverless edge routing support via `index.py`, utilizing dynamic temporary file handling (`/tmp`) for static media uploads in modern cloud runtimes.

### **Frontend (React 18 / Vite / Tailwind CSS):**
- **Framework & Build Engine:** React 18+ powered by Vite for instant Hot Module Replacement (HMR) and optimized distribution bundling.
- **State Management:** Layered React Context architecture (`AuthContext`, `RealTimeSyncContext`, `ToastContext`, and theme contexts) providing real-time UI reactions without redundant polling.
- **Styling:** Vanilla CSS integrated with custom Tailwind design tokens for rich glassmorphism, dynamic animations, and seamless dark mode experiences.

---

## 🗂️ Project Structure

```text
transitops-odoo-hackathon-2026/
├── backend/                        # FastAPI Enterprise Backend
│   ├── alembic/                    # Database schema migration scripts
│   ├── app/                  
│   │   ├── api/                    
│   │   │   ├── deps.py             # RBAC role checkers & auth token dependencies
│   │   │   └── v1/                 # REST API v1 Routers (auth, rbac, inventory, procurement, trips, reports, etc.)
│   │   ├── core/                   # Security (JWT hashing, config management, DB session lifecycle)
│   │   ├── models/                 # SQLAlchemy ORM entities (Users, Roles, Inventory, Trips, PermissionAuditLog)
│   │   ├── repositories/           # Data Access Layer implementing ACID-compliant Unit of Work
│   │   ├── schemas/                # Strict Pydantic validation models and matrix templates
│   │   └── services/               # Core business logic and event audit log generation
│   ├── scripts/                    # Automated database seeding and test data generators
│   ├── tests/                      # Exhaustive Pytest unit and regression testing suite
│   └── main.py                     # Application initialization & startup RBAC self-healing engine
├── frontend/                       # React 18 + Vite Enterprise Command Portal
│   ├── public/                     # Static media assets and branding files
│   ├── src/
│   │   ├── assets/                 # Global styling systems, fonts, and responsive utility CSS
│   │   ├── components/             # Reusable modular UI building blocks (Layouts, Sidebar, Modals, Tables)
│   │   ├── contexts/               # Global state providers (Authentication, RealTimeSync, Notifications)
│   │   ├── pages/                  # Route views (Dashboard, Vehicles, Trips, Inventory, RBAC Management)
│   │   ├── services/               # Axios REST API communication client with interceptors
│   │   └── utils/                  # Document exporters (PDF/CSV generator tools) & formatters
│   └── tests/                      # Playwright end-to-end (E2E) UI verification test specs
└── index.py                        # Root serverless execution entrypoint for cloud edge deployments (Vercel)
```

---

## ⚙️ Architecture Workflow & Request Lifecycle

TransitOps enforces a strict, modular four-tier layered architecture that cleanly decouples network interfaces, business logic, authorization governance, and relational data access.

```text
+-------------------+       +-------------------+       +-------------------+       +-------------------+
|  React 18 View    | ----> |  FastAPI Router   | ----> |  Service Layer    | ----> | Repository & ORM  |
|  (UI & Context)   | <---- |  (Pydantic/RBAC)  | <---- |  (Business Logic) | <---- | (PostgreSQL/ACID) |
+-------------------+       +-------------------+       +-------------------+       +-------------------+
```

### 1. Frontend Component Lifecycle
1. **Route Activation:** The user accesses a URL or clicks the deployed domain link. Visiting the root link (`/`) bypasses old localStorage caches and mounts the `Login` Showcase for zero-friction persona evaluation.
2. **Authenticated Actions:** Once authenticated, custom custom hooks and context providers emit authenticated HTTP requests via Axios with JWT bearer tokens.
3. **Reactive Real-Time UI:** `RealTimeSyncContext` handles dynamic state updates across active browser viewports without forced page reloads.

### 2. Backend Request & RBAC Verification Lifecycle
1. **API Router (`api/v1/`):** Receives incoming HTTP packets and evaluates security headers using `deps.py` dependencies (`RoleChecker`). Root superuser profiles obtain universal execution privileges, while specific operational roles are checked against the matrix.
2. **Service Execution (`services/`):** Validated requests enter business logic service classes where complex transactions (e.g., deducting inventory stock upon maintenance order completion, syncing trip statuses) are calculated. Any security or role mutations automatically emit immutable `PermissionAuditLog` entries.
3. **Repository Persistence (`repositories/`):** Database modifications execute within atomic SQLAlchemy sessions, guaranteeing zero data corruption and full ACID transaction compliance in PostgreSQL.

---

## 🧪 Testing, Quality & Verification

TransitOps undergoes strict code verification to maintain production resilience:
- **Comprehensive Backend Regression Tests:** Verified against an exhaustive Pytest suite covering authentication, RBAC boundaries, trip dispatches, inventory restocking, and financial PDF report generation.
- **End-to-End (E2E) Frontend Verification:** Playwright testing suites validate critical UI interactive flows across desktop and mobile form factors.
- **Type Safety & Linting:** Clean static type conformance across all service layers, ORM models, and REST endpoints.
- **Localized Synthetic Benchmarks:** Tested against massive Indian transport operational datasets (10,000+ telemetry logs, regional commercial vehicle specifications, and nationwide logistics transport corridors).

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites & Repository Clone
Ensure Python 3.10+, Node.js 18+, and PostgreSQL (or local SQLite) are installed on your workstation.
```bash
git clone https://github.com/ayus1234/transitops-odoo-hackathon-2026.git
cd transitops-odoo-hackathon-2026
```

### 2. Backend Execution (FastAPI)
```bash
cd backend
# Create and activate virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate | Unix/macOS: source .venv/bin/activate

# Install requirements and run database migrations
pip install -r requirements.txt
alembic upgrade head

# Launch the FastAPI server with auto-healing RBAC initialization
python -m uvicorn app.main:app --reload --port 8000
```
*API interactive swagger documentation will be available locally at `http://localhost:8000/docs`.*

### 3. Frontend Execution (React + Vite)
Open a new terminal window and start the frontend development server:
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:5173` in your web browser. You will be greeted immediately by the interactive **Login Showcase**, where you can select from any of the 13 enterprise demo accounts!

---

## 📖 Additional Documentation
For deeper dives into operational modeling, access control governance, and production deployments, consult:
- `42_PHASE_AUDIT_REPORT.md` - Complete 42-phase QA, authorization, and operational audit executed against frozen verified commit `2daf213`.
- `RBAC_PERMISSION_MATRIX.md` - Complete master matrix of all 13 canonical system roles and operational capabilities.
- `RBAC_TEST_REPORT.md` - Complete zero-trust security audit verification and regression test compliance report.
- `API_SPECIFICATION.md` - Complete list of REST API endpoints and JSON request/response payloads.
- `DATABASE_SCHEMA.md` - PostgreSQL Entity-Relationship diagrams and schema definitions.
- `PROJECT_STRUCTURE.md` - Comprehensive layout of internal service boundaries and dependencies.
- `PRODUCTION_READINESS.md` - System performance benchmarks, known limitations, and security architecture audits.
- `DEPLOYMENT.md` - Production server staging guide for Cloud Engines, Nginx, Gunicorn, and Vercel.
- `CHANGELOG.md` - Full release notes and improvement log for v1.1.0.
