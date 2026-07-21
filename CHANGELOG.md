# Changelog

All notable changes to the TransitOps ERP project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
