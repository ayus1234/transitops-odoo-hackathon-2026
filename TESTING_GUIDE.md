# TransitOps — Testing Strategy & Verification Guide

## Testing Layers

1. **Backend Unit & Service Tests**: Pytest test suites testing model constraints, business logic rules, repository operations, and API routers.
2. **Frontend Build Verification**: Vite production bundle compilation check (`npm run build`).
3. **End-to-End Specs**: Playwright browser specs validating real user flows, modal interactions, tab navigation, and responsive rendering.

---

## Running Backend Tests

```bash
cd backend
python -m pytest -v --tb=short
```

To run a specific test suite:
```bash
python -m pytest tests/test_vehicle_360.py -v
```

---

## Running Playwright End-to-End Tests

```bash
cd frontend
npx playwright test
```

To run a specific spec file:
```bash
npx playwright test tests/e2e/wave1_fleet_erp.spec.js --headed
```

---

## E2E Test Suite Index (`frontend/tests/e2e/`)

- `wave1_fleet_erp.spec.js`: Vehicle 360, Driver 360, Vendors Page, Documents Panel UI flows.
- `phase1_fleet.spec.js`: Basic Vehicle & Driver CRUD.
- `phase2_maintenance.spec.js`: Maintenance work orders & status transitions.
- `phase3_inventory.spec.js`: Stock tracking & procurement workflows.
- `phase4_reporting.spec.js`: Financial & operational reporting.
- `cross_module.spec.js`: Cross-module integration flows.
- `demo_login.spec.js`: Auth & role permissions.
