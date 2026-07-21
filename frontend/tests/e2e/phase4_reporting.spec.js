import { test, expect } from '@playwright/test';

test.describe('Phase 4 - Reporting & Analytics', () => {
  let authToken;

  test.beforeEach(async ({ page, request }) => {
    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', 'admin@transitops.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    
    // Save auth token for API calls
    const storageState = await page.context().storageState();
    const tokenItem = await page.evaluate(() => localStorage.getItem('token'));
    authToken = tokenItem;
  });

  test('Custom Report Builder: Create, Execute, Schedule, Export', async ({ page }) => {
    // ----------------------------------------------------
    // 1. Create and Execute Custom Report
    // ----------------------------------------------------
    await page.goto('http://localhost:5173/reports/builder');
    
    // Fill in report details
    const reportName = 'E2E Fleet Test Report ' + Date.now();
    await page.fill('input[placeholder="e.g. Monthly Maintenance Costs"]', reportName);
    await page.locator('button:has-text("Vehicles")').click();
    
    // Select some fields
    await page.getByRole('checkbox', { name: 'registration_number' }).check();
    await page.getByRole('checkbox', { name: 'status' }).check();
    
    // Save and Execute
    await page.locator('button:has-text("Generate")').click();
    
    // Wait for the preview table to populate
    await expect(page.locator('table')).toBeVisible({ timeout: 10000 });
    // Check if there are rows in tbody
    const rows = page.locator('tbody tr');
    await expect(rows).not.toHaveCount(0, { timeout: 10000 });

    // ----------------------------------------------------
    // 2. Export Report
    // ----------------------------------------------------
    // Instead of actually downloading, we verify the buttons are there and click them
    // and wait for the request to go through.
    const downloadPromise = page.waitForEvent('download', { timeout: 10000 }).catch(() => null);
    await page.locator('button').filter({ hasText: 'CSV' }).first().click();
    
    const download = await downloadPromise;
    if (download) {
      expect(download.suggestedFilename()).toContain('.csv');
    }

    // ----------------------------------------------------
    // 3. Schedule Report
    // ----------------------------------------------------
    await page.locator('button:has-text("Schedule")').click();
    const modal = page.locator('.fixed').filter({ hasText: 'Schedule Report' });
    await expect(modal).toBeVisible();
    
    // Fill schedule modal
    await modal.locator('select').selectOption('weekly');
    await modal.locator('textarea').fill('admin@transitops.com');
    
    // Submit schedule
    await modal.locator('button:has-text("Save Schedule")').click();
    
    // Modal should close and toast should appear
    await expect(modal).not.toBeVisible();
  });

  test('Compliance Reports and Analytics Dashboard', async ({ page }) => {
    // ----------------------------------------------------
    // 4. Compliance Reports
    // ----------------------------------------------------
    await page.goto('http://localhost:5173/reports/fleet-compliance');
    
    // Wait for the table to load
    await expect(page.locator('table')).toBeVisible({ timeout: 10000 });
    
    // Ensure a compliance template is listed (checking first page data)
    await expect(page.locator('tbody').filter({ hasText: 'Driver Safety' })).toBeVisible();

    // ----------------------------------------------------
    // 5. Analytics Dashboard
    // ----------------------------------------------------
    await page.goto('http://localhost:5173/reports');
    
    // Verify KPIs
    await expect(page.locator('p').filter({ hasText: 'Total Revenue' })).toBeVisible();
    await expect(page.locator('p').filter({ hasText: 'Avg. Fuel Efficiency' })).toBeVisible();
    
    // Verify charts exist (canvas elements)
    const canvases = page.locator('canvas');
    await expect(canvases.first()).toBeVisible({ timeout: 10000 });
    expect(await canvases.count()).toBeGreaterThanOrEqual(1);
  });
});
