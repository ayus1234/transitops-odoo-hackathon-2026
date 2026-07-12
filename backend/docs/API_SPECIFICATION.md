# TransitOps API Specification

## Overview
This document defines all REST API endpoints for the TransitOps platform.
Base URL: `http://localhost:8000/api/v1`

All endpoints (except authentication) require JWT authentication via `Authorization: Bearer <token>` header.

---

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### Pagination Response
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 150,
    "total_pages": 8
  }
}
```

---

## 1. Authentication

### 1.1 Login
**POST** `/auth/login`

**Request Body:**
```json
{
  "email": "admin@transitops.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "email": "admin@transitops.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": {
        "id": "uuid",
        "name": "Fleet Manager"
      }
    }
  }
}
```

**Errors:**
- `401`: Invalid credentials
- `400`: Validation error

---

### 1.2 Get Current User
**GET** `/auth/me`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "admin@transitops.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "role": {
      "id": "uuid",
      "name": "Fleet Manager",
      "permissions": {}
    },
    "is_active": true,
    "last_login": "2024-01-15T10:30:00Z"
  }
}
```

---

### 1.3 Logout
**POST** `/auth/logout`

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## 2. Dashboard

### 2.1 Get Dashboard KPIs
**GET** `/dashboard/kpis`

**Query Parameters:**
- `start_date` (optional): Filter start date (ISO 8601)
- `end_date` (optional): Filter end date (ISO 8601)

**Response:**
```json
{
  "success": true,
  "data": {
    "total_vehicles": 50,
    "available_vehicles": 25,
    "vehicles_on_trip": 20,
    "vehicles_in_maintenance": 5,
    "drivers_available": 30,
    "drivers_on_trip": 20,
    "active_trips": 20,
    "pending_trips": 8,
    "fleet_utilization_pct": 40.0,
    "today_fuel_cost": 45000.00,
    "maintenance_cost_mtd": 120000.00,
    "operational_cost_mtd": 450000.00
  }
}
```

---

### 2.2 Get Fleet Utilization Trend
**GET** `/dashboard/fleet-utilization-trend`

**Query Parameters:**
- `period` (optional): `7d`, `30d`, `90d` (default: `30d`)

**Response:**
```json
{
  "success": true,
  "data": [
    { "date": "2024-01-01", "utilization_pct": 45.5 },
    { "date": "2024-01-02", "utilization_pct": 48.2 }
  ]
}
```

---

### 2.3 Get Vehicle Status Distribution
**GET** `/dashboard/vehicle-status-distribution`

**Response:**
```json
{
  "success": true,
  "data": [
    { "status": "Available", "count": 25 },
    { "status": "On Trip", "count": 20 },
    { "status": "In Shop", "count": 5 }
  ]
}
```

---

## 3. Vehicles

### 3.1 List Vehicles
**GET** `/vehicles`

**Query Parameters:**
- `page` (default: 1)
- `page_size` (default: 20)
- `status` (optional): Filter by status
- `vehicle_type` (optional): Filter by type
- `search` (optional): Search by registration or name

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "registration_number": "DL-01-AB-1234",
      "vehicle_name": "Tata LPT 1618",
      "vehicle_type": "Truck",
      "capacity_kg": 5000.00,
      "current_odometer_km": 45000.00,
      "status": "Available",
      "fuel_type": "Diesel",
      "acquisition_cost": 2500000.00
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 50,
    "total_pages": 3
  }
}
```

---

### 3.2 Get Vehicle by ID
**GET** `/vehicles/{id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "registration_number": "DL-01-AB-1234",
    "vehicle_name": "Tata LPT 1618",
    "vehicle_type": "Truck",
    "manufacturer": "Tata Motors",
    "model": "LPT 1618",
    "year": 2022,
    "capacity_kg": 5000.00,
    "fuel_type": "Diesel",
    "current_odometer_km": 45000.00,
    "acquisition_cost": 2500000.00,
    "acquisition_date": "2022-06-15",
    "insurance_expiry": "2025-06-14",
    "status": "Available",
    "created_at": "2022-06-15T10:00:00Z",
    "updated_at": "2024-01-15T14:30:00Z"
  }
}
```

---

### 3.3 Create Vehicle
**POST** `/vehicles`

**Request Body:**
```json
{
  "registration_number": "DL-01-AB-1234",
  "vehicle_name": "Tata LPT 1618",
  "vehicle_type": "Truck",
  "manufacturer": "Tata Motors",
  "model": "LPT 1618",
  "year": 2022,
  "capacity_kg": 5000.00,
  "fuel_type": "Diesel",
  "current_odometer_km": 0,
  "acquisition_cost": 2500000.00,
  "acquisition_date": "2022-06-15",
  "insurance_expiry": "2025-06-14"
}
```

**Response:** Same as Get Vehicle by ID

**Errors:**
- `400`: Validation error (duplicate registration, invalid data)
- `403`: Permission denied

---

### 3.4 Update Vehicle
**PUT** `/vehicles/{id}`

**Request Body:** Same as Create (partial updates allowed)

**Response:** Same as Get Vehicle by ID

---

### 3.5 Delete Vehicle
**DELETE** `/vehicles/{id}`

**Response:**
```json
{
  "success": true,
  "message": "Vehicle deleted successfully"
}
```

**Errors:**
- `400`: Cannot delete (vehicle has active trips)
- `404`: Vehicle not found

---

### 3.6 Get Vehicle Trip History
**GET** `/vehicles/{id}/trips`

**Query Parameters:**
- `page`, `page_size`
- `status` (optional)

**Response:** Paginated list of trips

---

### 3.7 Get Vehicle Maintenance History
**GET** `/vehicles/{id}/maintenance`

**Response:** Paginated list of maintenance logs

---

### 3.8 Get Vehicle Fuel Logs
**GET** `/vehicles/{id}/fuel-logs`

**Response:** Paginated list of fuel logs

---

## 4. Drivers

### 4.1 List Drivers
**GET** `/drivers`

**Query Parameters:**
- `page`, `page_size`
- `status` (optional)
- `search` (optional): Search by name or license

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "user": {
        "first_name": "Rajesh",
        "last_name": "Kumar",
        "email": "rajesh@transitops.com",
        "phone_number": "+919876543210"
      },
      "license_number": "DL-1234567890",
      "license_category": "HMV",
      "license_expiry_date": "2026-12-31",
      "safety_score": 95.5,
      "total_trips": 245,
      "status": "Available"
    }
  ],
  "pagination": { }
}
```

---

### 4.2 Get Driver by ID
**GET** `/drivers/{id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user": {
      "id": "uuid",
      "first_name": "Rajesh",
      "last_name": "Kumar",
      "email": "rajesh@transitops.com",
      "phone_number": "+919876543210"
    },
    "license_number": "DL-1234567890",
    "license_category": "HMV",
    "license_issue_date": "2020-01-01",
    "license_expiry_date": "2026-12-31",
    "date_of_birth": "1985-05-15",
    "emergency_contact": "+919876543211",
    "safety_score": 95.5,
    "total_trips": 245,
    "status": "Available",
    "joined_date": "2020-03-01"
  }
}
```

---

### 4.3 Create Driver
**POST** `/drivers`

**Request Body:**
```json
{
  "user": {
    "email": "rajesh@transitops.com",
    "password": "securepassword",
    "first_name": "Rajesh",
    "last_name": "Kumar",
    "phone_number": "+919876543210"
  },
  "license_number": "DL-1234567890",
  "license_category": "HMV",
  "license_issue_date": "2020-01-01",
  "license_expiry_date": "2026-12-31",
  "date_of_birth": "1985-05-15",
  "emergency_contact": "+919876543211"
}
```

**Response:** Same as Get Driver by ID

---

### 4.4 Update Driver
**PUT** `/drivers/{id}`

**Request Body:** Partial update allowed

---

### 4.5 Delete Driver
**DELETE** `/drivers/{id}`

---

### 4.6 Get Driver Trip History
**GET** `/drivers/{id}/trips`

**Response:** Paginated list of trips

---

### 4.7 Get Driver Performance
**GET** `/drivers/{id}/performance`

**Response:**
```json
{
  "success": true,
  "data": {
    "total_trips": 245,
    "completed_trips_last_30_days": 18,
    "safety_score": 95.5,
    "average_fuel_efficiency": 8.5,
    "on_time_delivery_pct": 92.0
  }
}
```

---

## 5. Trips

### 5.1 List Trips
**GET** `/trips`

**Query Parameters:**
- `page`, `page_size`
- `status` (optional)
- `vehicle_id` (optional)
- `driver_id` (optional)
- `start_date`, `end_date` (optional)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "trip_number": "TRP-2024-00001",
      "vehicle": {
        "id": "uuid",
        "registration_number": "DL-01-AB-1234",
        "vehicle_name": "Tata LPT 1618"
      },
      "driver": {
        "id": "uuid",
        "name": "Rajesh Kumar",
        "license_number": "DL-1234567890"
      },
      "source": "Delhi",
      "destination": "Jaipur",
      "cargo_weight_kg": 4500.00,
      "planned_distance_km": 280.00,
      "planned_departure": "2024-01-15T06:00:00Z",
      "planned_arrival": "2024-01-15T12:00:00Z",
      "status": "Dispatched"
    }
  ],
  "pagination": { }
}
```

---

### 5.2 Get Trip by ID
**GET** `/trips/{id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "trip_number": "TRP-2024-00001",
    "vehicle": { },
    "driver": { },
    "source": "Delhi",
    "destination": "Jaipur",
    "cargo_weight_kg": 4500.00,
    "planned_distance_km": 280.00,
    "actual_distance_km": 285.50,
    "planned_departure": "2024-01-15T06:00:00Z",
    "actual_departure": "2024-01-15T06:15:00Z",
    "planned_arrival": "2024-01-15T12:00:00Z",
    "actual_arrival": "2024-01-15T12:30:00Z",
    "start_odometer_km": 45000.00,
    "end_odometer_km": 45285.50,
    "fuel_consumed_liters": 35.00,
    "status": "Completed",
    "notes": "Delivery completed successfully",
    "created_by": { },
    "created_at": "2024-01-14T10:00:00Z",
    "updated_at": "2024-01-15T12:30:00Z"
  }
}
```

---

### 5.3 Create Trip
**POST** `/trips`

**Request Body:**
```json
{
  "vehicle_id": "uuid",
  "driver_id": "uuid",
  "source": "Delhi",
  "destination": "Jaipur",
  "cargo_weight_kg": 4500.00,
  "planned_distance_km": 280.00,
  "planned_departure": "2024-01-15T06:00:00Z",
  "planned_arrival": "2024-01-15T12:00:00Z",
  "notes": "Handle with care"
}
```

**Response:** Same as Get Trip by ID

**Errors:**
- `400`: Validation error (cargo exceeds capacity, vehicle/driver unavailable)

---

### 5.4 Dispatch Trip
**POST** `/trips/{id}/dispatch`

**Request Body:**
```json
{
  "start_odometer_km": 45000.00
}
```

**Response:** Updated trip with status = "Dispatched"

**Business Logic:**
- Changes trip status to "Dispatched"
- Sets vehicle status to "On Trip"
- Sets driver status to "On Trip"

---

### 5.5 Complete Trip
**POST** `/trips/{id}/complete`

**Request Body:**
```json
{
  "end_odometer_km": 45285.50,
  "actual_distance_km": 285.50,
  "fuel_consumed_liters": 35.00,
  "notes": "Delivery completed successfully"
}
```

**Response:** Updated trip with status = "Completed"

**Business Logic:**
- Changes trip status to "Completed"
- Restores vehicle status to "Available"
- Restores driver status to "Available"
- Increments driver total_trips

---

### 5.6 Cancel Trip
**POST** `/trips/{id}/cancel`

**Request Body:**
```json
{
  "reason": "Customer request"
}
```

**Response:** Updated trip with status = "Cancelled"

**Business Logic:**
- Changes trip status to "Cancelled"
- Restores vehicle and driver to "Available"

---

### 5.7 Get Trip Expenses
**GET** `/trips/{id}/expenses`

**Response:** List of expenses associated with the trip

---

## 6. Maintenance

### 6.1 List Maintenance Logs
**GET** `/maintenance`

**Query Parameters:**
- `page`, `page_size`
- `status` (optional)
- `vehicle_id` (optional)
- `priority` (optional)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "maintenance_number": "MNT-2024-00001",
      "vehicle": {
        "id": "uuid",
        "registration_number": "DL-01-AB-1234",
        "vehicle_name": "Tata LPT 1618"
      },
      "maintenance_type": "Oil Change",
      "description": "Regular oil change and filter replacement",
      "priority": "Medium",
      "assigned_technician": "Suresh Sharma",
      "scheduled_date": "2024-01-20",
      "status": "Pending",
      "estimated_cost": 5000.00
    }
  ],
  "pagination": { }
}
```

---

### 6.2 Get Maintenance by ID
**GET** `/maintenance/{id}`

**Response:** Full maintenance log details

---

### 6.3 Create Maintenance Log
**POST** `/maintenance`

**Request Body:**
```json
{
  "vehicle_id": "uuid",
  "maintenance_type": "Oil Change",
  "description": "Regular oil change and filter replacement",
  "priority": "Medium",
  "assigned_technician": "Suresh Sharma",
  "scheduled_date": "2024-01-20",
  "estimated_cost": 5000.00,
  "odometer_at_maintenance": 45000.00
}
```

**Response:** Created maintenance log

---

### 6.4 Update Maintenance Status
**PATCH** `/maintenance/{id}/status`

**Request Body:**
```json
{
  "status": "In Progress"
}
```

**Response:** Updated maintenance log

**Business Logic:**
- If status changes to "In Progress", sets vehicle status to "In Shop"
- If status changes to "Completed", restores vehicle status to "Available"

---

### 6.5 Complete Maintenance
**POST** `/maintenance/{id}/complete`

**Request Body:**
```json
{
  "completed_date": "2024-01-22",
  "actual_cost": 4800.00,
  "notes": "Maintenance completed successfully"
}
```

**Response:** Completed maintenance log

---

## 7. Fuel Logs

### 7.1 List Fuel Logs
**GET** `/fuel-logs`

**Query Parameters:**
- `page`, `page_size`
- `vehicle_id` (optional)
- `start_date`, `end_date` (optional)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "vehicle": {
        "id": "uuid",
        "registration_number": "DL-01-AB-1234"
      },
      "trip": {
        "id": "uuid",
        "trip_number": "TRP-2024-00001"
      },
      "fuel_type": "Diesel",
      "quantity_liters": 50.00,
      "cost_per_liter": 90.00,
      "total_cost": 4500.00,
      "odometer_reading": 45100.00,
      "refuel_date": "2024-01-15T14:30:00Z",
      "station_name": "Indian Oil",
      "location": "Delhi"
    }
  ],
  "pagination": { }
}
```

---

### 7.2 Create Fuel Log
**POST** `/fuel-logs`

**Request Body:**
```json
{
  "vehicle_id": "uuid",
  "trip_id": "uuid",
  "fuel_type": "Diesel",
  "quantity_liters": 50.00,
  "cost_per_liter": 90.00,
  "odometer_reading": 45100.00,
  "refuel_date": "2024-01-15T14:30:00Z",
  "station_name": "Indian Oil",
  "location": "Delhi",
  "receipt_number": "RC-123456"
}
```

**Response:** Created fuel log

**Errors:**
- `400`: Fuel type mismatch with vehicle

---

### 7.3 Get Fuel Efficiency
**GET** `/fuel-logs/efficiency`

**Query Parameters:**
- `vehicle_id` (optional)
- `start_date`, `end_date` (optional)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "vehicle_id": "uuid",
      "registration_number": "DL-01-AB-1234",
      "avg_fuel_efficiency_kmpl": 8.5,
      "total_fuel_consumed": 350.00,
      "total_distance": 2975.00
    }
  ]
}
```

---

## 8. Expenses

### 8.1 List Expenses
**GET** `/expenses`

**Query Parameters:**
- `page`, `page_size`
- `expense_type` (optional)
- `vehicle_id` (optional)
- `trip_id` (optional)
- `status` (optional)
- `start_date`, `end_date` (optional)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "expense_type": "Toll",
      "vehicle": {
        "id": "uuid",
        "registration_number": "DL-01-AB-1234"
      },
      "trip": {
        "id": "uuid",
        "trip_number": "TRP-2024-00001"
      },
      "amount": 500.00,
      "expense_date": "2024-01-15",
      "description": "Highway toll - Delhi to Jaipur",
      "status": "Approved",
      "vendor_name": "NHAI"
    }
  ],
  "pagination": { }
}
```

---

### 8.2 Create Expense
**POST** `/expenses`

**Request Body:**
```json
{
  "expense_type": "Toll",
  "vehicle_id": "uuid",
  "trip_id": "uuid",
  "amount": 500.00,
  "expense_date": "2024-01-15",
  "description": "Highway toll - Delhi to Jaipur",
  "vendor_name": "NHAI",
  "receipt_number": "TOLL-12345"
}
```

**Response:** Created expense

---

### 8.3 Approve Expense
**PATCH** `/expenses/{id}/approve`

**Response:** Updated expense with status = "Approved"

---

### 8.4 Reject Expense
**PATCH** `/expenses/{id}/reject`

**Request Body:**
```json
{
  "reason": "Missing receipt"
}
```

**Response:** Updated expense with status = "Rejected"

---

### 8.5 Get Expense Summary
**GET** `/expenses/summary`

**Query Parameters:**
- `start_date`, `end_date` (optional)
- `vehicle_id` (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "total_expenses": 125000.00,
    "fuel_expenses": 75000.00,
    "maintenance_expenses": 40000.00,
    "toll_expenses": 8000.00,
    "repair_expenses": 2000.00,
    "miscellaneous_expenses": 0.00,
    "by_status": {
      "pending": 15000.00,
      "approved": 110000.00,
      "rejected": 0.00
    }
  }
}
```

---

## 9. Reports & Analytics

### 9.1 Fleet Utilization Report
**GET** `/reports/fleet-utilization`

**Query Parameters:**
- `start_date`, `end_date` (optional)
- `vehicle_type` (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    },
    "overall_utilization_pct": 42.5,
    "by_vehicle_type": [
      {
        "vehicle_type": "Truck",
        "total_vehicles": 30,
        "avg_utilization_pct": 45.0
      },
      {
        "vehicle_type": "Van",
        "total_vehicles": 20,
        "avg_utilization_pct": 38.5
      }
    ]
  }
}
```

---

### 9.2 Vehicle ROI Report
**GET** `/reports/vehicle-roi`

**Query Parameters:**
- `vehicle_id` (optional)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "vehicle_id": "uuid",
      "registration_number": "DL-01-AB-1234",
      "acquisition_cost": 2500000.00,
      "total_fuel_cost": 120000.00,
      "total_maintenance_cost": 50000.00,
      "total_other_expenses": 30000.00,
      "total_operational_cost": 200000.00,
      "total_trips": 85,
      "roi_pct": -8.0
    }
  ]
}
```

---

### 9.3 Driver Performance Report
**GET** `/reports/driver-performance`

**Query Parameters:**
- `driver_id` (optional)
- `start_date`, `end_date` (optional)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "driver_id": "uuid",
      "driver_name": "Rajesh Kumar",
      "total_trips": 245,
      "trips_in_period": 25,
      "safety_score": 95.5,
      "avg_fuel_efficiency": 8.5,
      "on_time_delivery_pct": 92.0
    }
  ]
}
```

---

### 9.4 Operational Cost Report
**GET** `/reports/operational-cost`

**Query Parameters:**
- `start_date`, `end_date` (optional)
- `group_by` (optional): `month`, `vehicle`, `expense_type`

**Response:**
```json
{
  "success": true,
  "data": {
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    },
    "total_cost": 450000.00,
    "by_expense_type": [
      { "expense_type": "Fuel", "total": 280000.00 },
      { "expense_type": "Maintenance", "total": 120000.00 },
      { "expense_type": "Toll", "total": 40000.00 },
      { "expense_type": "Repair", "total": 10000.00 }
    ]
  }
}
```

---

### 9.5 Fuel Consumption Report
**GET** `/reports/fuel-consumption`

**Query Parameters:**
- `vehicle_id` (optional)
- `start_date`, `end_date` (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "total_fuel_consumed": 3500.00,
    "total_fuel_cost": 315000.00,
    "avg_cost_per_liter": 90.00,
    "by_vehicle": [
      {
        "vehicle_id": "uuid",
        "registration_number": "DL-01-AB-1234",
        "fuel_consumed": 350.00,
        "fuel_cost": 31500.00,
        "avg_efficiency_kmpl": 8.5
      }
    ]
  }
}
```

---

### 9.6 Export Report
**GET** `/reports/{report_type}/export`

**Query Parameters:**
- `format`: `csv` or `pdf`
- All applicable filter parameters

**Response:**
- File download (CSV or PDF)

**Report Types:**
- `fleet-utilization`
- `vehicle-roi`
- `driver-performance`
- `operational-cost`
- `fuel-consumption`

---

## 10. Notifications

### 10.1 List User Notifications
**GET** `/notifications`

**Query Parameters:**
- `page`, `page_size`
- `is_read` (optional): `true` or `false`
- `notification_type` (optional)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "Trip Assigned",
      "message": "You have been assigned to trip TRP-2024-00001",
      "notification_type": "Trip Assigned",
      "is_read": false,
      "related_entity_type": "trip",
      "related_entity_id": "uuid",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "pagination": { }
}
```

---

### 10.2 Mark Notification as Read
**PATCH** `/notifications/{id}/read`

**Response:**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

---

### 10.3 Mark All as Read
**POST** `/notifications/mark-all-read`

**Response:**
```json
{
  "success": true,
  "message": "All notifications marked as read"
}
```

---

### 10.4 Get Unread Count
**GET** `/notifications/unread-count`

**Response:**
```json
{
  "success": true,
  "data": {
    "unread_count": 5
  }
}
```

---

## 11. Users & Settings

### 11.1 List Users
**GET** `/users`

**Query Parameters:**
- `page`, `page_size`
- `role_id` (optional)
- `is_active` (optional)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "email": "admin@transitops.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "+1234567890",
      "role": {
        "id": "uuid",
        "name": "Fleet Manager"
      },
      "is_active": true,
      "last_login": "2024-01-15T10:30:00Z",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "pagination": { }
}
```

---

### 11.2 Create User
**POST** `/users`

**Request Body:**
```json
{
  "email": "newuser@transitops.com",
  "password": "securepassword",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone_number": "+1234567891",
  "role_id": "uuid"
}
```

**Response:** Created user (without password)

---

### 11.3 Update User
**PUT** `/users/{id}`

**Request Body:** Partial update allowed (except password)

---

### 11.4 Deactivate User
**PATCH** `/users/{id}/deactivate`

**Response:**
```json
{
  "success": true,
  "message": "User deactivated successfully"
}
```

---

### 11.5 Change Password
**POST** `/users/{id}/change-password`

**Request Body:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

### 11.6 List Roles
**GET** `/roles`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Fleet Manager",
      "permissions": {
        "vehicles": ["read", "create", "update", "delete"],
        "drivers": ["read", "create", "update", "delete"],
        "trips": ["read", "create", "update", "delete"]
      }
    }
  ]
}
```

---

## 12. Validations & Business Rules

### Vehicle Registration
- Registration number must be unique
- Cannot register a vehicle with a duplicate registration number
- Status must be one of: Available, On Trip, In Shop, Retired

### Driver Management
- License number must be unique
- Cannot assign a driver with expired license to a trip
- Cannot assign a Suspended or Off Duty driver to a trip
- Status must be one of: Available, On Trip, Off Duty, Suspended

### Trip Creation & Dispatch
- Cargo weight must not exceed vehicle's maximum capacity
- Vehicle must be in "Available" status
- Driver must be in "Available" status
- Retired or In Shop vehicles cannot be dispatched
- Drivers with expired licenses cannot be assigned
- On dispatch: vehicle and driver status automatically change to "On Trip"

### Trip Completion
- End odometer must be >= start odometer
- Actual distance should be reasonable
- On completion: vehicle and driver status restore to "Available"
- Driver total_trips increments by 1

### Trip Cancellation
- Can only cancel trips in "Draft" or "Dispatched" status
- On cancellation: vehicle and driver status restore to "Available"

### Maintenance
- Creating maintenance with status "In Progress" sets vehicle to "In Shop"
- Vehicle in "In Shop" status cannot be dispatched
- Completing maintenance restores vehicle to "Available"

### Fuel Logs
- Fuel type must match vehicle's fuel type
- Total cost = quantity_liters × cost_per_liter
- Odometer reading should be >= vehicle's current odometer

### Expenses
- Amount must be positive
- Approved expenses cannot be modified
- Rejected expenses can be resubmitted with corrections

---

## 13. Error Codes

### Authentication Errors
- `AUTH_001`: Invalid credentials
- `AUTH_002`: Token expired
- `AUTH_003`: Invalid token
- `AUTH_004`: Insufficient permissions
- `AUTH_005`: Account deactivated

### Validation Errors
- `VAL_001`: Required field missing
- `VAL_002`: Invalid format
- `VAL_003`: Value out of range
- `VAL_004`: Duplicate entry
- `VAL_005`: Referenced entity not found

### Business Logic Errors
- `BIZ_001`: Vehicle already on trip
- `BIZ_002`: Driver already on trip
- `BIZ_003`: Cargo exceeds vehicle capacity
- `BIZ_004`: Vehicle not available (In Shop/Retired)
- `BIZ_005`: Driver license expired
- `BIZ_006`: Driver not available (Suspended/Off Duty)
- `BIZ_007`: Invalid status transition
- `BIZ_008`: Fuel type mismatch

### System Errors
- `SYS_001`: Database error
- `SYS_002`: Internal server error
- `SYS_003`: Service unavailable

---

## 14. Authentication & Authorization

### JWT Token Structure
```json
{
  "sub": "user_id",
  "email": "user@transitops.com",
  "role": "Fleet Manager",
  "permissions": {},
  "exp": 1705320000,
  "iat": 1705316400
}
```

### Token Expiration
- Access tokens expire after 1 hour (3600 seconds)
- Refresh tokens (optional): 7 days

### Protected Routes
All routes except `/auth/login` require authentication.

### Role-Based Access Control (RBAC)

**Fleet Manager:**
- Full access to all modules
- Can create, read, update, delete vehicles, drivers, trips
- Can approve expenses
- Can view all reports

**Driver:**
- Read access to assigned trips
- Can update trip status (start/complete)
- Can create fuel logs
- Can view own profile and performance

**Safety Officer:**
- Read access to drivers and trips
- Can update driver safety scores
- Can suspend drivers
- Can view driver performance reports

**Financial Analyst:**
- Read access to all expenses, fuel logs, maintenance costs
- Can view all financial reports
- Cannot modify operational data

### Permission Checks
The backend should validate permissions before executing operations:
```python
# Example
if user.role.name != "Fleet Manager":
    raise PermissionDenied("Insufficient permissions")
```

---

## 15. API Testing with Swagger

FastAPI automatically generates interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Use Swagger UI to test all endpoints during development.

---

## 16. Implementation Notes

### Auto-Generated IDs
- `trip_number`: `TRP-{YEAR}-{5-digit-sequence}` (e.g., TRP-2024-00001)
- `maintenance_number`: `MNT-{YEAR}-{5-digit-sequence}` (e.g., MNT-2024-00001)

### Timestamps
- All timestamps should be in ISO 8601 format with UTC timezone
- Example: `2024-01-15T10:30:00Z`

### Pagination
- Default page size: 20
- Maximum page size: 100
- Page numbers start at 1

### Filtering
- Support multiple filters combined with AND logic
- Date filters use ISO 8601 format

### Sorting
- Default sort: `created_at DESC`
- Support custom sorting via `sort_by` and `sort_order` query parameters

### Search
- Case-insensitive partial matching
- Searches across relevant text fields (names, numbers, descriptions)

---

## 17. Status Code Summary

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful delete) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (authentication required) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate entry) |
| 422 | Unprocessable Entity (business logic error) |
| 500 | Internal Server Error |

---

## 18. Rate Limiting (Optional)

For production deployments, consider implementing rate limiting:
- 100 requests per minute per user
- 1000 requests per hour per user

---

## 19. CORS Configuration

Allow requests from frontend origins:
```python
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://transitops.example.com"
]
```

---

## 20. Health Check

### Health Check Endpoint
**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

## Conclusion

This API specification provides a complete blueprint for implementing the TransitOps backend. 

Key highlights:
✅ RESTful design principles  
✅ Comprehensive CRUD operations  
✅ Business rule enforcement  
✅ Role-based access control  
✅ Detailed error handling  
✅ Analytics and reporting  
✅ Auto-generated documentation  

Use this specification to generate the FastAPI backend implementation with consistent patterns and proper validation.
