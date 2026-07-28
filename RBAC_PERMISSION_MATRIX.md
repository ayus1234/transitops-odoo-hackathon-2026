# TransitOps ERP — Master RBAC & Permission Matrix

This document defines the comprehensive **Role-Based Access Control (RBAC)** architecture and granular permission assignments for TransitOps ERP v1.0.0. All permissions are strictly enforced on the backend via authorization middlewares and database capabilities, adhering strictly to the **Principle of Least Privilege (PoLP)** and zero-trust security governance.

---

## 1. Enterprise Canonical System Roles (13 Roles)

TransitOps ERP comes with 13 canonical, protected system roles. None of these roles can be deleted or overwritten by custom role definitions, and universal administrative roles cannot have their security policies restricted.

| # | Canonical Role Name | Operational Scope & Responsibilities | Demo Email | Governance Level |
|---|---|---|---|---|
| **1** | **Super Admin** | Unrestricted access across all ERP modules, security auditing, RBAC policy management, user administration, and tenant governance. | `admin@transitops.com` | Universal Admin |
| **2** | **Administrator** | Enterprise administrative capabilities for configuring organization settings, module features, and global reporting oversight. | `administrator@transitops.com` | Universal Admin |
| **3** | **System Admin** | Technical platform control, infrastructure diagnostics, system logs, user technical administration, and backend integration control. | `sysadmin@transitops.com` | Universal Admin |
| **4** | **Fleet Manager** | Complete management of fleet assets, vehicle registries, driver assignments, trip execution oversight, fuel tracking, and maintenance operations. | `fleet@transitops.com` | Operational Admin |
| **5** | **Dispatcher** | Daily transit control: route creation, dispatching vehicles, driver assignments, real-time trip monitoring, and schedule adjustments. | `dispatcher@transitops.com` | Functional Specialist |
| **6** | **Maintenance Manager** | Oversight of workshop activities, preventive maintenance scheduling, technician assignments, job order tracking, and parts requisition approvals. | `maintenance@transitops.com` | Functional Specialist |
| **7** | **Technician** | Workshop field access: servicing vehicles, executing repair checklists, updating job progress, and submitting spare parts usage reports. | `technician@transitops.com` | Field Personnel |
| **8** | **Safety Officer** | Compliance and risk mitigation: tracking driver safety metrics, investigating transit incidents, performing compliance audits, and safety analytics. | `safety@transitops.com` | Compliance Officer |
| **9** | **Financial Analyst** | Financial accounting and auditing: fuel budgeting, expense ledger management, maintenance cost reconciliation, and financial analytics. | `finance@transitops.com` | Financial Reviewer |
| **10** | **Procurement Operations** | Supply chain administration: vendor management, spare parts purchasing, inventory stock reconciliation, and purchase order processing. | `procurement@transitops.com` | Functional Specialist |
| **11** | **HR/Operations** | Human resources administration: driver onboarding, staff registry updates, license verification, compliance tracking, and shift schedules. | `hr@transitops.com` | HR Personnel |
| **12** | **Support Agent** | Help center servicing: resolving support tickets, logging technical interactions, and diagnosing driver/operator user feedback. | `support@transitops.com` | Support Representative |
| **13** | **Driver** | Mobile driver portal access: viewing scheduled trips, reporting vehicle telemetry, logging trip expenses, and monitoring personal safety scorecards. | `driver@transitops.com` | Field Personnel |

---

## 2. Resource & Action Permission Matrix

Every user request to an API endpoint is authenticated via JWT token and verified against the canonical permissions matrix or via explicit operational RoleCheckers. Below is the mapping of resource actions (`create`, `read`, `update`, `delete`, `approve`, `export`) granted to each canonical role.

| Resource / Module | Super Admin / Administrator / System Admin | Fleet Manager | Dispatcher | Maintenance Manager | Technician | Safety Officer | Financial Analyst | Procurement Ops | HR/Operations | Support Agent | Driver |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **All Modules (`all`)** | **ALL** | `--` | `--` | `--` | `--` | `--` | `--` | `--` | `--` | `--` | `--` |
| **Vehicles (`vehicles`)** | **ALL** | **ALL** | R | R, U | R, U | R | R | R | R | R | R |
| **Drivers (`drivers`)** | **ALL** | **ALL** | R, U | R | R | R, U | R | `--` | **ALL** | R | R, U (Self) |
| **Trips (`trips`)** | **ALL** | **ALL** | **ALL** | R | `--` | R | R | `--` | R | R | R, U (Status) |
| **Maintenance (`maintenance`)**| **ALL** | **ALL** | R | **ALL** | C, R, U | R | R | R | `--` | R | C, R |
| **Inventory (`inventory`)** | **ALL** | **ALL** | R | **ALL** | C, R, U | `--` | R | **ALL** | `--` | R | `--` |
| **Procurement (`procurement`)**| **ALL** | **ALL** | `--` | C, R, U, A | R | `--` | R, A | **ALL** (C,R,U,D) | `--` | `--` | `--` |
| **Fuel / Expenses (`fuel`)** | **ALL** | **ALL** | C, R, U | C, R, U | C, R, U | R | **ALL** | R | `--` | `--` | C, R |
| **Safety / Compliance (`safety`)**| **ALL** | **ALL** | R | R | R | **ALL** | R | `--` | R, U | `--` | R (Self) |
| **Reports & Analytics (`reports`)**| **ALL** | **ALL** | R, E | R, E | R | R, E | **ALL** (R,E) | R, E | R, E | R | `--` |
| **Help Center (`help_center`)**| **ALL** | **ALL** | C, R, U | C, R, U | C, R, U | C, R, U | C, R, U | C, R, U | C, R, U | **ALL** | C, R |
| **System Settings (`settings`)**| **ALL** | R, U (Org) | `--` | `--` | `--` | `--` | `--` | `--` | R, U (Org) | `--` | `--` |
| **RBAC Policies (`rbac`)** | **ALL** | `--` | `--` | `--` | `--` | `--` | `--` | `--` | `--` | `--` | `--` |
| **Audit Logs (`audit`)** | **ALL** | R | `--` | `--` | `--` | R | R | `--` | R | `--` | `--` |

*Legend: C = Create/Post, R = Read/Get, U = Update/Put/Patch, D = Delete, A = Approve/Reject, E = Export/Download.*

---

## 3. Zero-Trust Architecture & Hardening Safeguards

To prevent privilege escalation and secure multi-tenant cloud enterprise environments, TransitOps enforces the following zero-trust architectural policies:

### A. Immutable Role Identities (No Runtime Mutation)
- **Eliminated Bypass:** Historical mock logins attempted to sync demo user profiles during authentication, leading to race conditions and corrupted password hashes.
- **Enforcement:** Authentication endpoints evaluate user identities directly from persistent database records without altering credentials or modifying authorization states at runtime.

### B. Complete Removal of Hardcoded Bypasses
- **Eliminated Bypass:** Previous implementations allowed arbitrary bypasses in `User.has_permission()`, automatically permitting unrestricted access to `dashboard`, `reports`, and `settings` for all accounts regardless of DB state.
- **Enforcement:** All resource requests are verified explicitly against the structured role capability map stored in Postgres/SQLAlchemy. If a resource capability is missing from the assigned role, access is instantaneously denied with an HTTP `403 Forbidden` response.

### C. True Cryptographic Audit Logs
- **Eliminated Bypass:** Application startups previously purged and seeded synthetic audit logs into memory or database storage to simulate compliance.
- **Enforcement:** Audit logging is strictly transaction-bound to authentic operations. All user authentication events, failed privilege attempts, resource updates, and RBAC policy modifications are recorded accurately with timestamps, client IP addresses, and acting user IDs.

### D. Protected Universal System Admin Roles
- The core administrative triad (**Super Admin**, **Administrator**, **System Admin**) is constitutionally shielded within the system. Their operational privileges (`{"all": ["create", "read", "update", "delete", "approve", "export"]}`) cannot be unassigned, restricted, or deleted via UI or API endpoints.
