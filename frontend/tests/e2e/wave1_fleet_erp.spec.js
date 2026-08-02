import { test, expect } from '@playwright/test';

test.describe('Wave 1 — Connected Fleet ERP End-to-End Suite', () => {

  test.beforeEach(async ({ page }) => {
    // Authenticate as Admin
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@transitops.com');
    await page.fill('input[type="password"]', 'admin123'); 
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('Vehicle 360 Profile Modal & Tab Navigation', async ({ page }) => {
    await page.goto('/vehicles');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Click 360 Profile button on first vehicle row
    const firstRow360Btn = page.locator('table tbody tr button[title="Vehicle 360 Profile"]').first();
    await expect(firstRow360Btn).toBeVisible({ timeout: 5000 });
    await firstRow360Btn.click();

    // Verify 360 Modal Header
    await expect(page.locator('h2').filter({ hasText: /Vehicle 360/i })).toBeVisible({ timeout: 5000 });

    // Test Tab 1: Specs breakdown
    await expect(page.locator('button').filter({ hasText: /Specs & Overview/i }).first()).toBeVisible();

    // Test Tab 2: Lifecycle Status
    const lifecycleTab = page.locator('button').filter({ hasText: /Lifecycle Status/i }).first();
    await lifecycleTab.click();
    await expect(page.getByText(/Current Lifecycle State/i)).toBeVisible();

    // Test Tab 3: Odometer History Log
    const odometerTab = page.locator('button').filter({ hasText: /Odometer History/i }).first();
    await odometerTab.click();
    await expect(page.getByText(/Odometer Reading Log/i)).toBeVisible();

    // Test Tab 4: Documents & Contracts
    const docsTab = page.locator('button').filter({ hasText: /Documents & Contracts/i }).first();
    await docsTab.click();

    // Test Tab 5: Total Cost of Ownership (TCO)
    const tcoTab = page.locator('button').filter({ hasText: /TCO Economics/i }).first();
    await tcoTab.click();
    await expect(page.getByText(/Operating Cost/i).first()).toBeVisible();

    // Close Modal
    await page.locator('div.fixed button').first().click();
    await page.waitForTimeout(300);
  });

  test('Driver 360 Profile Modal & Scorecards', async ({ page }) => {
    await page.goto('/drivers');
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Click 360 Profile button on first driver row
    const firstDriver360Btn = page.locator('table tbody tr button[title="Driver 360 Profile"]').first();
    await expect(firstDriver360Btn).toBeVisible({ timeout: 5000 });
    await firstDriver360Btn.click();

    // Verify Driver 360 Header
    await expect(page.getByText(/Licence & Compliance Info/i)).toBeVisible({ timeout: 5000 });

    // Test Tab 2: Performance Scorecard
    const perfTab = page.locator('button').filter({ hasText: /Performance Scorecard/i }).first();
    await perfTab.click();
    await expect(page.getByText(/Safety Score/i).first()).toBeVisible();
    await expect(page.getByText(/Efficiency Score/i).first()).toBeVisible();

    // Test Tab 3: Documents
    const driverDocsTab = page.locator('button').filter({ hasText: /Documents/i }).first();
    await driverDocsTab.click();

    // Close Modal
    await page.locator('div.fixed button').first().click();
    await page.waitForTimeout(300);
  });

  test('Vendor & Service Provider Directory', async ({ page }) => {
    await page.goto('/vendors');
    
    // Verify Page Header & KPI Cards
    await expect(page.locator('h1').filter({ hasText: /Vendor & Service Provider Directory/i })).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/Total Vendors/i)).toBeVisible();
    await expect(page.getByText(/Active Suppliers/i)).toBeVisible();

    // Open Add New Vendor Modal
    const addVendorBtn = page.locator('button').filter({ hasText: /Add New Vendor|Add Vendor|Register Vendor/i }).first();
    if (await addVendorBtn.isVisible()) {
      await addVendorBtn.click();
      await page.waitForTimeout(500);
    }

    // If vendors exist, test Scorecard drawer
    const scorecardBtn = page.locator('table tbody tr button[title="View Scorecard"]').first();
    if (await scorecardBtn.isVisible()) {
      await scorecardBtn.click();
      await expect(page.locator('h3').filter({ hasText: 'Vendor Scorecard' })).toBeVisible();
      await page.locator('div.fixed button span:has-text("close")').first().click();
    }
  });

});
