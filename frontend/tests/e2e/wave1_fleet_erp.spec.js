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

    // Test Tab 1: Specs & Specs breakdown
    await expect(page.getByRole('button', { name: /Vehicle Specs/i })).toBeVisible();

    // Test Tab 2: Lifecycle State Machine
    const lifecycleTab = page.getByRole('button', { name: /Lifecycle State/i });
    await lifecycleTab.click();
    await expect(page.getByText(/Allowed Lifecycle Transitions/i)).toBeVisible();

    // Test Tab 3: Odometer History Log
    const odometerTab = page.getByRole('button', { name: /Odometer Log/i });
    await odometerTab.click();
    await expect(page.getByText(/Current Vehicle Odometer/i)).toBeVisible();

    // Test Tab 4: Documents & Contracts
    const docsTab = page.getByRole('button', { name: /Documents & Contracts/i });
    await docsTab.click();
    await expect(page.getByText(/Attached Documents/i)).toBeVisible();

    // Test Tab 5: Total Cost of Ownership (TCO)
    const tcoTab = page.getByRole('button', { name: /Total Cost of Ownership/i });
    await tcoTab.click();
    await expect(page.getByText(/Total Cost of Ownership \(TCO\)/i)).toBeVisible();

    // Close Modal
    await page.locator('button span.material-symbols-outlined:has-text("close")').first().click();
    await expect(page.locator('h2').filter({ hasText: /Vehicle 360/i })).not.toBeVisible();
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
    const perfTab = page.getByRole('button', { name: /Performance Scorecard/i });
    await perfTab.click();
    await expect(page.getByText(/Safety Score/i)).toBeVisible();
    await expect(page.getByText(/Efficiency Score/i)).toBeVisible();

    // Test Tab 3: Documents
    const docsTab = page.getByRole('button', { name: /Documents/i });
    await docsTab.click();
    await expect(page.getByText(/Attached Documents/i)).toBeVisible();

    // Close Modal
    await page.locator('button span.material-symbols-outlined:has-text("close")').first().click();
  });

  test('Vendor & Service Provider Directory', async ({ page }) => {
    await page.goto('/vendors');
    
    // Verify Page Header & KPI Cards
    await expect(page.locator('h1').filter({ hasText: /Vendor & Service Provider Directory/i })).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/Total Vendors/i)).toBeVisible();
    await expect(page.getByText(/Active Suppliers/i)).toBeVisible();

    // Open Add New Vendor Modal
    await page.getByRole('button', { name: /Add New Vendor/i }).click();
    await expect(page.locator('h3').filter({ hasText: 'Add New Vendor' })).toBeVisible();

    // Close Modal
    await page.getByRole('button', { name: /Cancel/i }).click();
    await expect(page.locator('h3').filter({ hasText: 'Add New Vendor' })).not.toBeVisible();

    // If vendors exist, test Scorecard drawer
    const scorecardBtn = page.locator('table tbody tr button[title="View Scorecard"]').first();
    if (await scorecardBtn.isVisible()) {
      await scorecardBtn.click();
      await expect(page.locator('h3').filter({ hasText: 'Vendor Scorecard' })).toBeVisible();
      await page.locator('div.fixed button span:has-text("close")').first().click();
    }
  });

});
