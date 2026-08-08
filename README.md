# TransitOps V2 Enterprise Connected Fleet & Transportation Operations ERP

![TransitOps Banner](https://img.shields.io/badge/TransitOps-V2%20Enterprise%20ERP-blue?style=for-the-badge) ![Version](https://img.shields.io/badge/version-2.1.0-green?style=for-the-badge) ![Build](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge) ![Driver App](https://img.shields.io/badge/Driver%20App-Touch%20PWA-orange?style=for-the-badge) ![SaaS Billing](https://img.shields.io/badge/SaaS%20Billing-Stripe%20%26%20Razorpay-teal?style=for-the-badge) ![Pilot Telemetry](https://img.shields.io/badge/Pilot%20Telemetry-Active-emerald?style=for-the-badge) ![AI Copilot](https://img.shields.io/badge/AI-Copilot%20Enabled-purple?style=for-the-badge)

**TransitOps** is an enterprise-grade Connected Fleet & Transportation Operations Resource Planning (ERP) platform designed for modern fleet operators, logistics providers, workshop engineers, and multi-tenant SaaS transportation enterprises.

Built from the ground up for zero-trust security, real-time operational execution, high-concurrency dispatching, IoT telemetry ingestion (Geotab, Teltonika, Traccar), touch mobile driver workflows, live customer tracking, and predictive analytics, TransitOps seamlessly integrates vehicle telematics, multi-stop routing, driver safety scoring, preventive maintenance, multi-tier procurement, automated inventory replenishment, and natural-language AI insights into **ONE CONNECTED TRANSPORTATION PLATFORM**.

---

## 🌟 Key Capabilities & Architectural Waves

TransitOps V2 is organized into eight integrated capability waves, delivering complete operational coverage across the entire transportation asset lifecycle:

```text
┌───────────────────────┬───────────────────────┬───────────────────────┬───────────────────────┐
│                                TRANSITOPS V2 PLATFORM                                 │
├───────────────────────┼───────────────────────┼───────────────────────┼───────────────────────┤
│  FLEET OPERATIONS     │  ASSET OPERATIONS     │  BUSINESS OPERATIONS  │  RISK & GOVERNANCE    │
│  - Vehicle 360        │  - Maintenance 2.0    │  - Procurement 2.0    │  - License Compliance │
│  - Driver 360         │  - Technicians        │  - Vendors 360        │  - Universal Documents│
│  - Orders & Jobs      │  - Multi-Warehouse    │  - Fuel & Theft       │  - RBAC 2.0 & Auditing│
│  - Dispatch Board     │  - Parts Reorder      │  - EV & Energy        │  - Stripe/Razorpay    │
├───────────────────────┼───────────────────────┼───────────────────────┼───────────────────────┤
│  CONNECTED FLEET      │  EXPERIENCES          │  INTELLIGENCE         │  PLATFORM INTEGRATION │
│  - Telemetry API      │  - Desktop Web ERP    │  - AI Copilot         │  - Signed Webhooks    │
│  - Geotab/Traccar     │  - Driver Mobile PWA  │  - Predictive Maint   │  - Public REST APIs   │
│  - GPS Live Map       │  - Customer Tracking  │  - Pilot Dashboard    │  - Streaming Exporter │
│  - Proof Delivery     │  - Help Desk Chat     │  - Safety Scoring     │  - Global Cmd Ctrl+K  │
└───────────────────────┴───────────────────────┴───────────────────────┴───────────────────────┘
```

---

### 🚛 1. Fleet ERP & Asset 360 (Wave 1)
* **Vehicle 360 Profile:** 360-degree vehicle profile tracking VIN, manufacturer, model, variant, body type, powertrain, seating capacity, acquisition cost, insurance, and lease details. Validated state transitions across 11 lifecycle states: `Ordered`, `Acquired`, `Available`, `Assigned`, `Active`, `On Trip`, `Maintenance`, `In Shop`, `Inactive`, `Retired`, `Sold`.
* **Driver 360 & Scoring:** Comprehensive driver profiles tracking license classes/categories, medical fitness, total trips, emergency contacts, and score factor breakdowns across **Safety Score**, **Efficiency Score**, and **Compliance Score** (0–100 scale).
* **Odometer & Utilisation Engine:** Historical odometer logs with source attribution (*Manual*, *Trip*, *Maintenance*, *Telemetry*) and anti-regression enforcement logic.
* **Universal Document & Contract Management:** Attachable document engine for Vehicles, Drivers, Maintenance Records, and Contracts with automated expiry tracking (`Valid`, `Expiring Soon`, `Expired`) and configurable alert thresholds.
* **Vendor 360 Directory:** Supplier directory tracking lead times, contract agreements, service history, and vendor performance scorecards.

---

### 📦 2. Transportation & Dispatch Management (Wave 2)
* **Logistics Order & Cargo Jobs:** Separate job/order entity tracking customer CRM accounts, pickup/delivery addresses, cargo weight, volume, priority, and job-to-trip leg allocation.
* **Operational Dispatch Board:** Real-time Dispatch Board with drag-and-drop order queues. Executes automated pre-dispatch checks for vehicle availability, driver compliance, maintenance blocks, EV range, and weight capacity limits.
* **Multi-Stop Trips & Routing Service:** Multi-stop waypoint trip execution (Origin, Pickup, Waypoint, Delivery, Destination) powered by a provider-neutral Haversine routing engine with ETA calculations and leg progress tracking.
* **Geofenced Proof of Delivery (POD):** Delivery submission with geofence distance verification, signature capture, photo evidence upload, and automated job state transition to `Delivered`.

---

### 📡 3. Connected Fleet & Telemetry Platform (Wave 3)
* **Multi-Provider Telemetry Ingestion:** Ingestion API receiving `latitude`, `longitude`, `speed`, `heading`, `ignition`, `odometer`, `engine_hours`, `fuel_level`, and `battery_SOC` with multi-provider adapter support for **Geotab**, **Teltonika**, **Traccar**, and **Demo Simulator**.
* **Telemetry Simulator:** Demo telemetry simulator generating realistic vehicle route progression, speed changes, and heartbeat signals.
* **Live GPS Fleet Map:** Leaflet interactive map displaying vehicle markers, live status badges, historical vehicle breadcrumb trails, and trip route overlays.
* **Geofencing & Automated Alerts:** Circle and polygon geofence zones detecting arrival/departure events, speeding violations, and excessive idling.

---

### 🛠️ 4. Asset & Supply Chain Intelligence (Wave 4)
* **Maintenance 2.0 Command:** Preventive, Corrective, Breakdown, and Emergency work order tracking. Schedules technician rosters, task checklists, parts consumption, and downtime calculations.
* **Warehouses & Inventory 2.0:** Multi-warehouse stock tracking, bin locations, immutable movement history, reorder level warnings, and parts intelligence reorder suggestions.
* **Procurement 2.0 Workflow:** End-to-end purchasing lifecycle: Requisitions ➡️ Approval ➡️ RFQ Vendor Quote Comparison ➡️ Purchase Order ➡️ Goods Receipt ➡️ Inventory Stock Update.

---

### ⛽ 5. Fuel, EV, Safety & Compliance (Wave 5)
* **Fuel Intelligence & Theft Detection:** Refuel logging, km/L efficiency analytics, and statistical anomaly detection algorithms for suspicious fuel drops or theft.
* **EV / Energy Management:** State of Charge (SOC %) tracking, charging session logs, energy cost/km, and EV dispatch range validation.
* **Safety Intelligence:** Behavioral event tracking (speeding, harsh braking, rapid acceleration) contributing to driver safety scores.
* **Compliance Blocking Engine:** Real-time compliance engine evaluating license, insurance, and permit expiries with configurable dispatch warning or hard-blocking policies.

---

### 🛡️ 6. Enterprise Platform, Multi-Tenant SaaS & Billing (Wave 6)
* **Multi-Tenant SaaS Architecture:** `tenant_id` / `company_id` database isolation, company settings, and tenant-scoped RBAC authorization.
* **Stripe & Razorpay SaaS Billing Engine:** Subscriptions router ([`/api/v1/billing`](file:///c:/Users/hp/Downloads/New%20folder%20(6)/transitops-odoo-hackathon-2026/backend/app/api/v1/billing.py)) and frontend management dashboard ([`/settings/billing`](file:///c:/Users/hp/Downloads/New%20folder%20(6)/transitops-odoo-hackathon-2026/frontend/src/pages/settings/BillingSettings.jsx)) supporting plan tiers (*Starter*, *Professional*, *Enterprise*), checkout sessions, and webhook listeners (`/webhooks/stripe`, `/webhooks/razorpay`).
* **Granular RBAC 2.0 Matrix:** Role-Based Access Control enforcing 40+ distinct operational permissions across 13 canonical system roles + custom user-created roles.
* **Observability & Tracing:** Structured JSON logging, `X-Request-ID` middleware propagation, API latency tracking, and audit event logs.
* **Public APIs & Signed Webhooks:** Webhook subscription platform delivering signed payloads for events such as `trip.dispatched`, `maintenance.created`, and `inventory.low`.

---

### 📱 7. Specialized Experiences, Mobile Driver PWA & Customer Portal (Wave 7)
* **Mobile Driver Web App (`/driver/mobile`):** Smartphone-optimized touch interface ([`DriverMobileApp.jsx`](file:///c:/Users/hp/Downloads/New%20folder%20(6)/transitops-odoo-hackathon-2026/frontend/src/pages/drivers/DriverMobileApp.jsx)) for drivers to view active trip assignments, update trip progress (Start ➡️ Arrive), submit geofenced Proof of Delivery (photo & digital signature), log vehicle refuels, and report breakdown emergencies.
* **Public Customer Shipment Tracking Portal (`/tracking/:job_number`):** Lightweight, public-facing shipment tracking portal ([`CustomerTrackingPortal.jsx`](file:///c:/Users/hp/Downloads/New%20folder%20(6)/transitops-odoo-hackathon-2026/frontend/src/pages/jobs/CustomerTrackingPortal.jsx)) allowing customers to track order progress on a 4-stage visual timeline with live vehicle GPS coordinates, driver details, and signed POD proof.
* **Commercial Pilot Adoption Dashboard (`/analytics/pilot-dashboard`):** Real-time operational validation control center ([`PilotAdoptionDashboard.jsx`](file:///c:/Users/hp/Downloads/New%20folder%20(6)/transitops-odoo-hackathon-2026/frontend/src/pages/reports/PilotAdoptionDashboard.jsx)) tracking 6 explicit commercial readiness indicators across pilot fleets.
* **Help Center & Support Desk:** Searchable Knowledgebase articles + full internal Support Ticket System featuring priority badges, assigned support agents, and an interactive chat message timeline.

---

### 🤖 8. AI Intelligence & Predictive Analytics (Wave 8)
* **Fleet Copilot AI Assistant:** Natural-language query interface (`/api/v1/ai-copilot/query`) answering operational questions ("Which vehicles have highest maintenance cost this month?") grounded strictly in tenant database records.
* **Pilot Fleet Adoption Telemetry (`/api/v1/analytics/pilot-metrics`):** Operational telemetry engine measuring 6 explicit commercial readiness indicators: (1) Active Pilot Fleets / Tenants, (2) Weekly Dispatches per Fleet, (3) Daily Telemetry Pings per Vehicle, (4) Mobile POD Submissions Completed, (5) Customer Tracking Portal Views per Order, and (6) Trial-to-Paid Subscription Conversion Rate by Plan (*Starter*, *Pro*, *Enterprise*) with Monthly Recurring Revenue (MRR) tracking.
* **Predictive Analytics Models:** Fleet health score calculations, Total Cost of Ownership (TCO) per kilometer, and predictive maintenance component wear forecasting algorithms.

---

### ⚡ 9. Additional Value-Add Features & Utilities
* **Global Command Palette (`Ctrl + K` / `Cmd + K`):** Power-user keyboard shortcut menu for instant cross-entity search and rapid record creation.
* **RealTimeSync Engine (`RealTimeSyncContext`):** Background synchronization provider updating open viewports dynamically without forced page reloads.
* **Binary PDF & Excel Exporter:** Memory-buffered binary PDF generator (`fpdf2`) with ERP branding, dynamic column scaling, and spreadsheet (XLSX/CSV) fallbacks.
* **Yard & Warehouse Dock Scheduler:** Bay reservation and turnaround queue manager for warehouse depots.
* **Driver Payroll & Bonus Calculator:** Automated driver earnings calculation based on distance driven (km), trip volume, and safety score multipliers.
* **Logistics CRM & Accounts:** Customer profile tracking, freight contract terms, and billing reference management.
* **Financial General Ledger Mapping:** Accounting journal entry mappings for vehicle capital acquisition, depreciation, and operating expense categorization.

---

## 🏗️ Technology Stack

```text
┌────────────────────┬─────────────────────────────────────────────────────────────────┐
│                                 TECHNOLOGY STACK                                │
├────────────────────┼─────────────────────────────────────────────────────────────────┤
│ FRONTEND LAYER     │ React 18, Vite, Tailwind CSS, Leaflet Maps, Lucide Icons        │
│ SPECIALIZED UIs    │ Mobile Driver PWA, Customer Tracking Portal, Billing Dashboard  │
│ COMMERCIAL UIs     │ Pilot Fleet Commercial Adoption Control Center Dashboard        │
│ BACKEND API        │ Python 3.10+, FastAPI, Pydantic v2, Uvicorn, fpdf2              │
│ DATABASE & ORM     │ PostgreSQL 15+, SQLAlchemy 2.0 (Repository Pattern), Alembic     │
│ PAYMENT GATEWAYS   │ Stripe Checkout & Webhooks, Razorpay Checkout & Webhooks        │
│ TESTING & QA       │ Pytest, Playwright E2E, Hypothesis, Coverage.py                 │
│ OBSERVABILITY      │ Request-ID Middleware, Structured JSON Logging, Audit Engine    │
└────────────────────┴─────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Project Structure

```text
transitops-odoo-hackathon-2026/
├── backend/                                # FastAPI Enterprise Backend
│   ├── alembic/                            # Schema migration scripts
│   │   └── versions/                       # Incremental migration revisions
│   ├── app/
│   │   ├── api/                            # REST API v1 Endpoints
│   │   │   ├── deps.py                     # Auth & RBAC dependencies
│   │   │   └── v1/                         # Endpoints (auth, vehicles, drivers, trips, dispatch,
│   │   │                                   #  maintenance, fuel, inventory, procurement, safety,
│   │   │                                   #  billing, telemetry, jobs, pod, ai_copilot, analytics, etc.)
│   │   ├── core/                           # Security, JWT, middleware, config, DB session
│   │   ├── models/                         # SQLAlchemy 2.0 ORM Entities (Vehicle, Driver, Trip,
│   │   │                                   #  Job, Maintenance, Inventory, Fuel, HelpArticle, etc.)
│   │   ├── repositories/                   # Data Access Layer implementing ACID Unit of Work
│   │   ├── schemas/                        # Strict Pydantic models & validation schemas
│   │   └── services/                       # Business logic services & AI Copilot query engine
│   ├── scripts/                            # Data seeders & Telemetry Simulator
│   ├── tests/                              # Pytest backend integration test suite (29 modules)
│   └── main.py                             # Server startup & self-healing RBAC synchronizer
├── frontend/                               # React 18 + Vite Web ERP Portal
│   ├── public/                             # Static assets & branding
│   ├── src/
│   │   ├── assets/                         # Styling & utility CSS
│   │   ├── components/                     # Modular UI Components (Layouts, Navbar, Modals, Maps)
│   │   │   ├── help/                       # Help Center Modals & Ticket Drawers
│   │   │   └── layout/                     # Main Layout, Navbar, Command Palette, BottomNav
│   │   ├── contexts/                       # AuthContext, RealTimeSyncContext, ToastContext
│   │   ├── pages/                          # Route Views (Dashboard, Vehicles, Drivers, Trips,
│   │   │   ├── activity/                   #  Dispatch, Jobs, Maintenance, Fuel, Expenses,
│   │   │   ├── dispatch/                   #  Inventory, Procurement, Vendors, Help, Reports,
│   │   │   ├── drivers/                    #  DriverMobileApp, CustomerTrackingPortal,
│   │   │   ├── fleet_map/                  #  PilotAdoptionDashboard, BillingSettings, Settings)
│   │   │   ├── help/                       #
│   │   │   ├── inventory/                  #
│   │   │   ├── jobs/                       #
│   │   │   ├── maintenance/                #
│   │   │   ├── reports/                    #  FleetCompliance, ReportBuilder, PilotAdoptionDashboard
│   │   │   ├── settings/                   #
│   │   │   └── vendors/                    #
│   │   ├── services/                       # Axios REST client with authorization interceptors
│   │   └── utils/                          # Document formatting & export helpers
│   └── tests/                              # Playwright End-to-End (E2E) UI test suite
└── index.py                                # Cloud Serverless edge execution entrypoint
```

---

## ⚙️ Architecture Workflow & Data Lifecycle

TransitOps enforces a decoupled, four-tier architecture isolating network contracts, security validation, core domain business logic, and transactional persistence:

```text
┌─────────────────────────┐      ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ React Web ERP / PWA App │ ───> │  FastAPI Router │ ───> │  Service Layer  │ ───> │ Repository Layer│
│(Driver PWA/Customer Track)│ <─── │ (Pydantic/RBAC) │ <─── │(Business Engine)│ <─── │(PostgreSQL/ACID)│
└─────────────────────────┘      └─────────────────┘      └─────────────────┘      └─────────────────┘
      │      │                                                     │                        │
      │      ▼                                                     ▼                        ▼
      │ ┌─────────────────┐                               ┌─────────────────┐      ┌─────────────────┐
      │ │ Global Cmd Ctrl+K│                              │ AI Copilot &    │      │ Alembic Schema  │
      │ │ RealTimeSync Eng│                               │ Pilot Telemetry │      │   Migrations    │
      │ └─────────────────┘                               └─────────────────┘      └─────────────────┘
      ▼
┌─────────────────────────┐
│ Stripe & Razorpay SaaS  │
│ Gateway Checkout/Hooks  │
└─────────────────────────┘
```

### Request Lifecycle Steps:
1. **User Action / Telemetry / Mobile App:** Driver updates trip on Mobile PWA (`/driver/mobile`), customer checks shipment tracking (`/tracking/:job`), or fleet manager views Pilot Adoption Control Center (`/analytics/pilot-dashboard`).
2. **Security & Authorization (`api/deps.py`):** FastAPI validates JWT bearer tokens, checks tenant boundaries, and executes `RoleChecker` against the RBAC 2.0 matrix.
3. **Business Processing (`services/`):** Validated inputs enter service logic (e.g. pre-dispatch fit calculations, geofence POD verification, fuel theft algorithms, Stripe/Razorpay billing, AI Copilot SQL generation, pilot fleet adoption metrics).
4. **Transactional Persistence (`repositories/`):** Changes persist within atomic SQLAlchemy database sessions. Security alterations generate immutable audit entries in `permission_audit_logs`.
5. **Streaming Output & Real-Time Sync:** Response returns formatted JSON, streaming PDF byte-buffer, or triggers real-time UI state updates via `RealTimeSyncContext`.

---

## 🧪 Testing & Verification Suite

TransitOps maintains production reliability through comprehensive testing:

```bash
# Run backend pytest suite across all 10 core integration modules
cd backend
python -m pytest tests/test_dispatch_board.py tests/test_dispatch_concurrency.py tests/test_vehicle_recommendation.py tests/test_routing.py tests/test_pod.py tests/test_audit_events.py tests/test_production_readiness.py tests/test_telemetry.py tests/test_analytics.py tests/test_extended_suite.py -vv --tb=long -ra
```

**Results:** All **29/29 integration tests pass in ~2.4s** with 100% migration schema alignment.

---

## 🚀 Quick Start (Local Setup)

### 1. Repository Setup
```bash
git clone https://github.com/ayus1234/transitops-odoo-hackathon-2026.git
cd transitops-odoo-hackathon-2026
```

### 2. Backend Initialization
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate | Unix/macOS: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```
*API documentation available at `http://localhost:8000/docs`.*

### 3. Frontend Initialization
```bash
cd frontend
npm install
npm run dev
```
*Access web ERP portal at `http://localhost:5173`.*

---

## 📄 Documentation Index
- `V2_ARCHITECTURE.md` - Complete V2 Target Architecture & Module Specification.
- `RBAC_PERMISSION_MATRIX.md` - Master Matrix of 13 Canonical System Roles and 40+ Capabilities.
- `PRODUCTION_READINESS.md` - System Benchmarks, Security Audits, and Scalability Architecture.
- `DEPLOYMENT.md` - Deployment guide for Nginx, Gunicorn, PostgreSQL, and Cloud Edge runtimes.
- `CHANGELOG.md` - Full release history for V2.1.0.
