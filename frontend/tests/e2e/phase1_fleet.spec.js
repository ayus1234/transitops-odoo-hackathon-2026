import { test, expect } from '@playwright/test';

test.describe('Phase 1 - Fleet Management', () => {

  test.beforeEach(async ({ page }) => {
    // Authenticate
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@transitops.com');
    await page.fill('input[type="password"]', 'admin123'); 
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('Vehicles: CRUD Operations', async ({ page }) => {
    const timestamp = Date.now();
    const testReg = `TEST-${timestamp}`;
    const testName = `Phase1 Truck ${timestamp}`;

    await page.goto('/vehicles');
    
    // 1. Create Vehicle
    await page.getByRole('button', { name: /Add Vehicle/i }).click();
    await expect(page.locator('h2').filter({ hasText: 'Register New Vehicle' })).toBeVisible({ timeout: 5000 });
    
    await page.fill('input[name="registration_number"]', testReg);
    await page.fill('input[name="vehicle_name"]', testName);
    await page.fill('input[name="capacity_kg"]', '25000');
    
    // Save Vehicle
    await page.click('button:has-text("Save Vehicle")');
    
    // Verify Modal closes
    await expect(page.locator('h2').filter({ hasText: 'Register New Vehicle' })).not.toBeVisible({ timeout: 8000 });
    
    // 2. Read / Search Vehicle
    const searchInput = page.getByPlaceholder('Search vehicles...');
    await searchInput.fill(testReg);
    await page.waitForTimeout(1000); // Wait for debounce/API
    
    // Assert row exists
    await expect(page.locator(`table tbody tr:has-text("${testReg}")`)).toBeVisible();
    
    // 3. Update Vehicle
    // Wait for the row to be visible
    const updatedRow = page.locator('table tbody tr').filter({ hasText: testName });
    await expect(updatedRow).toBeVisible({ timeout: 5000 });
    
    await updatedRow.locator('button[title="Edit Vehicle"]').click();
    
    await expect(page.locator('h2').filter({ hasText: 'Edit Vehicle' })).toBeVisible({ timeout: 5000 });
    await page.fill('input[name="vehicle_name"]', `${testName} UPDATED`);
    await page.click('button:has-text("Save Vehicle")');
    await expect(page.locator('h2').filter({ hasText: 'Edit Vehicle' })).not.toBeVisible({ timeout: 8000 });
    
    // 4. Delete Vehicle
    // Re-search to find the updated row
    await page.fill('input[placeholder="Search vehicles..."]', `${testName} UPDATED`);
    const rowToDelete = page.locator('table tbody tr').filter({ hasText: `${testName} UPDATED` });
    await expect(rowToDelete).toBeVisible({ timeout: 5000 });
    
    await rowToDelete.locator('button[title="Delete Vehicle"]').click();
    
    // Confirm delete in dialog
    await page.locator('button.bg-error', { hasText: 'Delete' }).click();
  });

  test('Drivers: CRUD Operations & Filtering', async ({ page }) => {
    const timestamp = Date.now();
    const testLicense = `LIC-${timestamp}`;
    const testName = `John Test ${timestamp}`;

    await page.goto('/drivers');
    
    // 1. Create Driver
    await page.getByRole('button', { name: /Add Driver/i }).click();
    await expect(page.locator('h2').filter({ hasText: 'Onboard New Driver' })).toBeVisible({ timeout: 5000 });
    
    await page.fill('input[name="full_name"]', `John Test ${timestamp}`);
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.fill('input[name="email"]', `john.test.${timestamp}@example.com`);
    await page.fill('input[name="license_number"]', testLicense);
    await page.fill('input[name="license_issue_date"]', '2023-01-01');
    await page.fill('input[name="license_expiry_date"]', '2033-01-01');
    await page.fill('input[name="date_of_birth"]', '1990-01-01');
    
    await page.click('button:has-text("Save Driver")');
    await expect(page.locator('h2').filter({ hasText: 'Onboard New Driver' })).not.toBeVisible({ timeout: 8000 });
    
    // 2. Filter & Search
    const searchInput = page.getByPlaceholder('Search drivers, license or phone...');
    await searchInput.fill(timestamp.toString());
    
    // 3. Update Driver
    const updatedRow = page.locator('table tbody tr').filter({ hasText: timestamp.toString() });
    await expect(updatedRow).toBeVisible({ timeout: 5000 });
    
    await updatedRow.locator('button[title="Edit Driver"]').click();
    
    await expect(page.locator('h2').filter({ hasText: 'Edit Driver' })).toBeVisible({ timeout: 5000 });
    await page.fill('input[name="emergency_contact"]', `+15550001234`);
    await page.click('button:has-text("Save Driver")');
    await expect(page.locator('h2').filter({ hasText: 'Edit Driver' })).not.toBeVisible({ timeout: 8000 });
    
    // 4. Delete Driver
    await searchInput.fill(timestamp.toString());
    const rowToDelete = page.locator('table tbody tr').filter({ hasText: timestamp.toString() });
    await expect(rowToDelete).toBeVisible({ timeout: 5000 });
    
    await rowToDelete.locator('button[title="Delete Driver"]').click();
    
    // Confirm delete in dialog
    await page.locator('button.bg-error', { hasText: 'Delete' }).click();
    
    // Export Check
    const exportBtn = page.getByRole('button', { name: /Export/i });
    if (await exportBtn.isVisible()) {
        await exportBtn.click();
        await page.click('text=Export CSV');
    }
  });

});
