# TransitOps — System Architecture & Technical Specification

## Overview
TransitOps is a modular, high-performance Connected Fleet & Transportation Operations ERP built to scale from single-depot dispatch to multi-company enterprise logistics.

---

## Technical Stack Summary

| Layer | Technology | Key Responsibilities |
|---|---|---|
| **Frontend SPA** | React 18, Vite 8, TailwindCSS, Axios, Lucide/Material Symbols | Single Page ERP Application, responsive data tables, modal drawers, dynamic dashboards |
| **Backend REST API** | FastAPI (Python 3.12+), Pydantic V2, Uvicorn | Async HTTP APIs, RBAC permission enforcement, business domain services |
| **ORM & Database** | SQLAlchemy 2.0, PostgreSQL 15+, Alembic | Relational data mapping, ACID transactional integrity, Alembic migration chains |
| **Security & Auth** | JWT (HS256), Passlib (Bcrypt), OAuth2 Password Bearer | Token authentication, 13 canonical roles, granular resource-level permission matrix |
| **Testing** | Pytest, Playwright, Hypothesis | End-to-end regression, API specification testing, cross-browser validation |

---

## Core Domain Layering

```
                     ┌───────────────────────────────┐
                     │    React SPA / Web Client     │
                     └───────────────┬───────────────┘
                                     │ HTTP REST (JSON)
                                     ▼
                     ┌───────────────────────────────┐
                     │    FastAPI Application Core   │
                     │  (Routers / Dependencies)     │
                     └───────────────┬───────────────┘
                                     │ PermissionChecker / Security
                                     ▼
                     ┌───────────────────────────────┐
                     │     Business Service Layer    │
                     │ (VehicleService, Driver, etc) │
                     └───────────────┬───────────────┘
                                     │ Business Rule Enforcement
                                     ▼
                     ┌───────────────────────────────┐
                     │      Repository Layer         │
                     │  (Encapsulated DB Queries)    │
                     └───────────────┬───────────────┘
                                     │ SQLAlchemy ORM
                                     ▼
                     ┌───────────────────────────────┐
                     │     PostgreSQL Database       │
                     └───────────────────────────────┘
```

---

## Functional Layers (V2 Product ERP)

1. **Fleet Operations**: Vehicles, Vehicle 360, Driver 360, Trips, Jobs, Dispatch Board, Telemetry Ingestion.
2. **Asset Operations**: Maintenance 2.0, Work Orders, Parts & Inventory, Warehouses, Equipment, Service Vendors.
3. **Business Operations**: Procurement 2.0, Vendors Directory, Purchase Orders, Fuel Intelligence, Expenses & TCO.
4. **Risk & Governance**: Safety Events, Compliance Engine, Document & Contract Management, RBAC 2.0, Audit Logs.
5. **Intelligence Layer**: Fleet Copilot, Automation Engine, Analytics & Forecasting.
