# TransitOps — Database Schema & Data Dictionary

## Overview
TransitOps utilizes PostgreSQL with SQLAlchemy 2.0 ORM. All schema evolution is managed via linear Alembic migrations.

---

## Core Entities & Models

### 1. `vehicles`
- `id` (UUID, PK)
- `registration_number` (VARCHAR 50, UNIQUE, INDEX)
- `vehicle_name` (VARCHAR 255)
- `vehicle_type` (VARCHAR 50) — Truck, Bus, Van, Container, etc.
- `capacity_kg` (NUMERIC 10,2)
- `fuel_type` (VARCHAR 50) — Diesel, Petrol, Electric, Hybrid, CNG
- `current_odometer_km` (NUMERIC 10,2)
- `status` (VARCHAR 50) — `Ordered`, `Acquired`, `Available`, `Assigned`, `Active`, `On Trip`, `Maintenance`, `Inactive`, `Retired`, `Sold`
- **Vehicle 360 Columns**: `vin`, `variant`, `body_type`, `powertrain`, `ownership_type`, `lease_provider`, `lease_start_date`, `lease_end_date`, `monthly_lease_cost`, `engine_hours`, `retired_date`, `sale_price`

### 2. `drivers`
- `id` (UUID, PK)
- `user_id` (UUID, FK → `users.id`, UNIQUE)
- `license_number` (VARCHAR 50, UNIQUE)
- `license_category` (VARCHAR 50)
- `license_issue_date`, `license_expiry_date` (DATE)
- `safety_score`, `efficiency_score`, `compliance_score`, `overall_score` (NUMERIC 5,2)
- **Driver 360 Columns**: `license_class`, `blood_group`, `medical_fitness_expiry`, `current_vehicle_id` (FK → `vehicles.id`)

### 3. `odometer_readings`
- `id` (UUID, PK)
- `vehicle_id` (UUID, FK → `vehicles.id`, INDEX)
- `reading_km` (NUMERIC 10,2)
- `recorded_at` (TIMESTAMP WITH TIME ZONE)
- `source` (VARCHAR 20) — `manual`, `trip`, `maintenance`, `telemetry`, `correction`
- `recorded_by` (UUID, FK → `users.id`)
- `trip_id` (UUID, FK → `trips.id`, nullable)

### 4. `documents`
- `id` (UUID, PK)
- `document_type` (VARCHAR 50) — `registration`, `insurance`, `fitness`, `pollution`, `permit`, `licence`, `warranty`, `lease_contract`, `service_agreement`
- `document_number` (VARCHAR 100)
- `title` (VARCHAR 255)
- `expiry_date` (DATE, INDEX)
- `status` (VARCHAR 20) — `Active`, `Expired`, `Revoked`, `Draft`
- `verification_state` (VARCHAR 20) — `Unverified`, `Verified`, `Rejected`
- **Polymorphic FKs**: `vehicle_id`, `driver_id`, `vendor_id`, `maintenance_id`

### 5. `vendors`
- `id` (UUID, PK)
- `vendor_code` (VARCHAR 50, UNIQUE, INDEX)
- `name` (VARCHAR 255, INDEX)
- `categories` (JSONB) — `["Parts", "Service", "Fuel", "Tyres", "Insurance"]`
- `rating` (NUMERIC 3,2)
- `is_active` (BOOLEAN)

---

## Alembic Migration Revision Chain
`20261207_vehicle` $\rightarrow$ ... $\rightarrow$ `5ce577173c60` $\rightarrow$ `a1b2c3d4e5f6` (Vehicle 360) $\rightarrow$ `b2c3d4e5f6a7` (Odometer) $\rightarrow$ `c3d4e5f6a7b8` (Documents) $\rightarrow$ `d4e5f6a7b8c9` (Driver 360) $\rightarrow$ `e5f6a7b8c9d0` (Vendors - **HEAD**).
