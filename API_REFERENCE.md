# TransitOps — REST API Reference & Endpoint Index

## Base URL
`/api/v1`

---

## 1. Fleet Operations

### Vehicles & Vehicle 360
- `GET /vehicles` — List vehicles with search & filters (`page`, `page_size`, `status`, `vehicle_type`, `search`)
- `POST /vehicles` — Register a new vehicle
- `GET /vehicles/{id}` — Get vehicle details
- `PUT /vehicles/{id}` — Update vehicle record
- `DELETE /vehicles/{id}` — Delete vehicle (blocked if `On Trip`, `In Shop`, or `Maintenance`)
- `GET /vehicles/{id}/360` — Get Vehicle 360 profile (specs, lifecycle state machine, odometer, documents, TCO)
- `PATCH /vehicles/{id}/status` — Validated status transition (`new_status`, `reason`, `retired_date`, `sale_price`)
- `GET /vehicles/{id}/tco` — Calculate full Total Cost of Ownership breakdown

### Odometer History
- `POST /vehicles/{id}/odometer` — Record odometer reading with anti-regression check
- `GET /vehicles/{id}/odometer` — Get paginated odometer history
- `GET /vehicles/{id}/odometer/stats` — Get distance & utilisation metrics

### Drivers & Driver 360
- `GET /drivers` — List drivers with search & filters
- `POST /drivers` — Onboard new driver & user account
- `GET /drivers/{id}` — Get driver profile
- `PUT /drivers/{id}` — Update driver details
- `DELETE /drivers/{id}` — Suspend/delete driver
- `GET /drivers/{id}/360` — Comprehensive Driver 360 profile
- `GET /drivers/performance` — Driver performance metrics breakdown

---

## 2. Document & Vendor Management

### Documents
- `GET /documents` — List documents filtered by entity (`vehicle_id`, `driver_id`, `vendor_id`, `maintenance_id`)
- `POST /documents` — Store document metadata
- `POST /documents/upload` — Upload document file binary
- `PATCH /documents/{id}/verify` — Verify or reject document
- `GET /documents/expiring` — Get documents expiring within threshold days

### Vendors
- `GET /vendors` — List vendors filtered by category and active status
- `POST /vendors` — Create new vendor supplier / service workshop
- `GET /vendors/{id}` — Get vendor details
- `PUT /vendors/{id}` — Update vendor profile
- `DELETE /vendors/{id}` — Delete vendor
- `GET /vendors/{id}/scorecard` — Vendor performance scorecard
