import { test, expect } from '@playwright/test';

test.describe('Phase 7.1 - Smoke Testing', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to login
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@transitops.com');
    await page.fill('input[type="password"]', 'admin123'); // Assume default password
    await page.click('button[type="submit"]');
    // Wait for navigation to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('Dashboard loads correctly', async ({ page }) => {
    // Verify Dashboard title
    await expect(page.locator('h1').filter({ hasText: 'Operations Dashboard' })).toBeVisible({ timeout: 10000 });
    // Verify KPI Row exists (check for Total text)
    await expect(page.locator('text=Total').first()).toBeVisible();
    // Verify Maintenance Table exists
    await expect(page.locator('h2').filter({ hasText: 'Upcoming Maintenance' })).toBeVisible();
  });

  test('Navigation sidebar links work', async ({ page }) => {
    // Click on Vehicles
    await page.click('a[href="/vehicles"]');
    await expect(page.locator('h1').filter({ hasText: 'Vehicle Registry' })).toBeVisible({ timeout: 10000 });

    // Click on Drivers
    await page.click('a[href="/drivers"]');
    await expect(page.locator('h1').filter({ hasText: 'Driver Management' })).toBeVisible({ timeout: 10000 });
  });

  test('Fleet Map initializes', async ({ page }) => {
    await page.goto('/fleet-map/full');
    await expect(page.locator('h1').filter({ hasText: 'Live Fleet Map' })).toBeVisible({ timeout: 10000 });
    // Verify Leaflet container is present
    await expect(page.locator('.leaflet-container')).toBeVisible();
  });

  test('Reports module loads', async ({ page }) => {
    await page.goto('/reports');
    await expect(page.locator('h1').filter({ hasText: 'Reports & Analytics' })).toBeVisible({ timeout: 10000 });
  });

  test('Settings and Permissions load', async ({ page }) => {
    await page.goto('/settings');
    await expect(page.locator('h1').filter({ hasText: 'Settings' })).toBeVisible({ timeout: 10000 });
    
    // Check if roles tab exists
    await expect(page.locator('text=Role Management')).toBeVisible();
  });

});
