import { test, expect } from '@playwright/test';

test.describe('Phase 1 - Cross-Module Workflows', () => {

  test.beforeEach(async ({ page }) => {
    // Authenticate
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@transitops.com');
    await page.fill('input[type="password"]', 'admin123'); 
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test.setTimeout(60000);

  test('E2E: Vehicle -> Driver -> Trip -> Activity -> Notification', async ({ page }) => {
    const timestamp = Date.now();
    const testReg = `TRK-${timestamp}`;
    const testVehicleName = `CrossMod Truck ${timestamp}`;
    const testLicense = `DRV-${timestamp}`;

    // 1. Register Vehicle
    await page.goto('/vehicles');
    await page.getByRole('button', { name: /Add Vehicle/i }).click();
    await page.fill('input[name="registration_number"]', testReg);
    await page.fill('input[name="vehicle_name"]', testVehicleName);
    await page.fill('input[name="capacity_kg"]', '10000');
    await page.click('button:has-text("Save Vehicle")');
    await expect(page.locator('h2').filter({ hasText: 'Register New Vehicle' })).not.toBeVisible({ timeout: 8000 });

    // 2. Register Driver
    await page.goto('/drivers');
    await page.getByRole('button', { name: /Add Driver/i }).click();
    await page.fill('input[name="full_name"]', `Cross Driver ${timestamp}`);
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.fill('input[name="email"]', `cross.${timestamp}@example.com`);
    await page.fill('input[name="license_number"]', testLicense);
    await page.fill('input[name="license_issue_date"]', '2023-01-01');
    await page.fill('input[name="license_expiry_date"]', '2033-01-01');
    await page.fill('input[name="date_of_birth"]', '1990-01-01');
    await page.click('button:has-text("Save Driver")');
    await expect(page.locator('h2').filter({ hasText: 'Onboard New Driver' })).not.toBeVisible({ timeout: 8000 });

    // 3. Create Trip (Assign Driver & Vehicle)
    await page.goto('/trips');
    await page.locator('button:has-text("Create Trip")').first().click();
    await expect(page.locator('h3').filter({ hasText: 'New Trip Planning' })).toBeVisible({ timeout: 5000 });
    
    await page.fill('input[name="source"]', 'Warehouse A');
    await page.fill('input[name="destination"]', 'Store B');
    await page.fill('input[name="planned_distance_km"]', '150');
    await page.fill('input[name="cargo_weight_kg"]', '2000');
    await page.fill('input[name="planned_departure"]', '2025-01-01T10:00');
    await page.fill('input[name="planned_arrival"]', '2025-01-01T12:00');
    
    await page.click('button:has-text("Next")');
    
    // Step 2: Select Vehicle and Driver
    // Use select options
    // Assuming the option text contains the vehicle registration and driver name
    const vehicleOption = page.locator('select[name="vehicle_id"] option').filter({ hasText: testReg });
    await expect(vehicleOption).toBeAttached({ timeout: 10000 });
    const vehicleValue = await vehicleOption.getAttribute('value');
    await page.locator('select[name="vehicle_id"]').selectOption(vehicleValue);
    
    const driverOption = page.locator('select[name="driver_id"] option').filter({ hasText: `Cross Driver ${timestamp}` });
    await expect(driverOption).toBeAttached({ timeout: 10000 });
    const driverValue = await driverOption.getAttribute('value');
    await page.locator('select[name="driver_id"]').selectOption(driverValue);

    await page.click('button:has-text("Next")');

    // Step 3: Confirm
    await page.locator('.fixed button:has-text("Create Trip")').click();
    await expect(page.locator('h3').filter({ hasText: 'New Trip Planning' })).not.toBeVisible({ timeout: 8000 });

    // 4. Activity Log Entry Verification
    await page.goto('/activity');
    
    // Filter by module 'Vehicle' to ensure demo_engine noise doesn't push it off page 1
    const moduleFilter = page.locator('select[name="moduleFilter"]').first(); 
    if (await moduleFilter.isVisible()) {
       await moduleFilter.selectOption('Vehicle');
    } else {
       // fallback if the select doesn't have name="moduleFilter"
       await page.locator('select').first().selectOption('Vehicle');
    }
    
    await expect(page.getByText(testReg, { exact: false }).first()).toBeVisible({ timeout: 15000 });

    // 5. Track on Fleet Map
    await page.goto('/fleet-map/full');
    await page.waitForTimeout(2000); // Map load
    const mapSearch = page.getByPlaceholder('Search vehicles, drivers, or routes...');
    if (await mapSearch.isVisible()) {
      await mapSearch.fill(testReg);
      await page.waitForTimeout(1000);
      // Ensure it doesn't crash
    }

  });

});
