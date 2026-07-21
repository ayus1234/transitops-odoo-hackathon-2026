import { test, expect } from '@playwright/test';

test.describe('Phase 2 - Maintenance Operations', () => {

  test.beforeEach(async ({ page }) => {
    // Authenticate
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@transitops.com');
    await page.fill('input[type="password"]', 'admin123'); 
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('Maintenance Workflow: Create -> Update Status -> Complete', async ({ page }) => {
    
    // LOG NETWORK AND CONSOLE TO DEBUG
    page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));
    page.on('response', response => {
      if(response.url().includes('/maintenance')) {
        console.log('NETWORK:', response.request().method(), response.url(), response.status());
      }
    });

    const timestamp = Date.now();
    const testReg = `TRK-${timestamp}-MNT`;
    const testVehicleName = `MNT Truck ${timestamp}`;
    const testDescription = `Brake pad replacement ${timestamp}`;

    // 0. Register unique vehicle for maintenance isolation
    await page.goto('/vehicles');
    await page.getByRole('button', { name: /Add Vehicle/i }).click();
    await page.fill('input[name="registration_number"]', testReg);
    await page.fill('input[name="vehicle_name"]', testVehicleName);
    await page.fill('input[name="capacity_kg"]', '10000');
    await page.click('button:has-text("Save Vehicle")');
    await expect(page.locator('h2').filter({ hasText: 'Register New Vehicle' })).not.toBeVisible({ timeout: 8000 });

    await page.goto('/maintenance');
    
    // 1. Schedule Maintenance
    await page.click('button:has-text("New Service Record")');
    await expect(page.locator('h2').filter({ hasText: 'New Service Record' })).toBeVisible({ timeout: 5000 });
    
    // Select the unique vehicle
    const vehicleOption = page.locator('select[name="vehicle_id"] option').filter({ hasText: testReg });
    await expect(vehicleOption).toBeAttached({ timeout: 10000 });
    const vehicleValue = await vehicleOption.getAttribute('value');
    await page.locator('select[name="vehicle_id"]').selectOption(vehicleValue);

    await page.locator('select[name="maintenance_type"]').selectOption({ label: 'Brake Service' });
    await page.fill('input[name="description"]', testDescription);
    await page.locator('select[name="priority"]').selectOption({ label: 'High' });
    
    await page.click('button:has-text("Save Record")');
    await expect(page.locator('h2').filter({ hasText: 'New Service Record' })).not.toBeVisible({ timeout: 8000 });

    // 2. Verify creation in table
    const recordRow = page.locator('tr').filter({ hasText: testDescription }).first();
    await expect(recordRow).toBeVisible({ timeout: 8000 });
    
    // 3. Update Maintenance Status to 'Approved'
    await recordRow.locator('button[title="Update Status"]').click();
    await expect(page.locator('h2').filter({ hasText: 'Update Status' })).toBeVisible({ timeout: 5000 });
    await page.locator('select[name="status"]').selectOption({ label: 'Approved' });
    await page.locator('.fixed button:has-text("Confirm")').click();
    await expect(page.locator('h2').filter({ hasText: 'Update Status' })).not.toBeVisible({ timeout: 8000 });
    await expect(recordRow.locator('span:has-text("SCHEDULED")')).toBeVisible({ timeout: 5000 }); // Approved shows as SCHEDULED in UI

    // 4. Update Maintenance Status to 'In Progress'
    await recordRow.locator('button[title="Update Status"]').click();
    await expect(page.locator('h2').filter({ hasText: 'Update Status' })).toBeVisible({ timeout: 5000 });
    await page.locator('select[name="status"]').selectOption({ label: 'In Progress' });
    await page.locator('.fixed button:has-text("Confirm")').click();
    await expect(page.locator('h2').filter({ hasText: 'Update Status' })).not.toBeVisible({ timeout: 8000 });

    // Verify it is In Progress
    await expect(recordRow.locator('span:has-text("IN PROGRESS")')).toBeVisible({ timeout: 5000 });

    // 5. Complete Maintenance
    // Click the Complete button (has title="Complete")
    await recordRow.locator('button[title="Complete"]').click();
    await expect(page.locator('h2').filter({ hasText: 'Complete Maintenance' })).toBeVisible({ timeout: 5000 });
    
    await page.fill('input[name="actual_cost"]', '450.50');
    await page.fill('textarea[name="notes"]', 'Replaced all brake pads');
    
    await page.locator('.fixed button:has-text("Confirm")').click();
    await expect(page.locator('h2').filter({ hasText: 'Complete Maintenance' })).not.toBeVisible({ timeout: 8000 });
    
    // Verify it is completed (Status badge should change to Completed)
    await expect(recordRow.locator('span:has-text("COMPLETED")')).toBeVisible({ timeout: 5000 });
  });

});
