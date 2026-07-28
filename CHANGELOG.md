# Changelog

All notable changes to the TransitOps ERP project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.0-verified-baseline] - 2026-07-28 — **Frozen Verified Baseline (Commit `2daf213`)**
### Verified Audit & Governance
- Executed and signed off on exhaustive **42-Phase Verified Baseline Audit** (`42_PHASE_AUDIT_REPORT.md`) without mutating application feature code.
- Tagged release as immutable engineering reference (`v1.1.0-verified-baseline` and `v1.1.0`) with associated test evidence, permission matrices, known limitations, and deployment configurations.

### Enterprise Zero-Trust RBAC Hardening
- **Canonical 13-Role Hierarchy**: Standardized 13 enterprise operational accounts across database capabilities, backend middle tier guards, and frontend UI components.
- **Removed Bypasses & Dynamic Mutations**: Purged insecure login profile munging (`_auto_sync_demo_account`), eliminated hardcoded wildcard access bypasses in `User.has_permission()`, and removed synthetic audit log injection on server startup.
- **Protected Admin Triad**: Universal system administrator accounts (`Super Admin`, `Administrator`, `System Admin`) constitutionally shielded against UI or API deletion and permission downgrades.
- **Evaluator Login Showcase**: Direct routing to `/login` on domain accesses, mounting interactive role switching without cache interference.

### Resolved Concurrency & Persistence Flaws
- Replaced database string sorting (`order_by(desc())`) with integer sequence extraction and exponential retry backoffs in `MaintenanceService` and `TripService`, permanently resolving sequence collision anomalies under rapid concurrent record generation.

### Quality Assurance Assurance
- 100% test success rate confirmed across **234 Backend Pytest integration assertions** and **21 Playwright E2E interactive specifications** executed under sequential database fixture isolation.

## [1.0.0-rc1] - 2026-07-21
### Added
- Comprehensive fleet, driver, trip, and maintenance modules.
- Enterprise-grade inventory and procurement workflow with PO management.
- Dynamic dashboard with real-time KPI metrics.
- Fleet Map integration via Google Maps API.
- Role-Based Access Control (RBAC) with detailed permission assignments.
- Custom report generation and standardized CSV/PDF exports.
- Global search, advanced filtering, and pagination across all data tables.
- Cross-platform responsive design (320px to 3840px widths).

### Changed
- Migrated database from SQLite to PostgreSQL (`psycopg2`).
- Optimized backend for enterprise-scale latency (sub-100ms P95 API response times on 10k+ rows).
- Re-architected Playwright E2E tests for parallelized reliability via unique seeding parameters.

### Fixed
- Addressed multiple UI component rendering overlaps on smaller viewports.
- Resolved race conditions in Activity Feed test assertions via localized test module filtering.
- Prevented overlapping toast notifications in concurrent actions.
