import { test, expect } from '@playwright/test';

test.describe('Feature 2.2 — Operations Control Center & Dispatch Board E2E Suite', () => {

  test.beforeEach(async ({ page }) => {
    // Authenticate
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@transitops.com');
    await page.fill('input[type="password"]', 'admin123'); 
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('Dispatch Control Tower: View Queues, Asset Selection & Run Pre-Dispatch Safety Check', async ({ page }) => {
    // 1. Navigate to Dispatch Board
    await page.goto('/dispatch');
    await expect(page.locator('h1').filter({ hasText: /Operations Control Center/i })).toBeVisible({ timeout: 5000 });

    // 2. Verify Real-time KPI Overview Bar
    await expect(page.getByText('Jobs Waiting').first()).toBeVisible();
    await expect(page.getByText('Available Vehicles').first()).toBeVisible();
    await expect(page.getByText('Available Drivers').first()).toBeVisible();
    await expect(page.getByText('Active Trips').first()).toBeVisible();

    // 3. Select first job in Column 1 (if available)
    const firstJobCard = page.locator('div:has-text("1. Select Customer Job") ~ div div[class*="cursor-pointer"]').first();
    if (await firstJobCard.isVisible()) {
      await firstJobCard.click();
    }

    // 4. Select first vehicle in Column 2 (if available)
    const firstVehicleCard = page.locator('div:has-text("Available Vehicles") ~ div div[class*="cursor-pointer"]').first();
    if (await firstVehicleCard.isVisible()) {
      await firstVehicleCard.click();
    }

    // 5. Select first driver in Column 2 (if available)
    const firstDriverCard = page.locator('div:has-text("Available Drivers") ~ div div[class*="cursor-pointer"]').first();
    if (await firstDriverCard.isVisible()) {
      await firstDriverCard.click();
    }

    // 6. Test Safety Check button
    const validateBtn = page.getByRole('button', { name: /Run Pre-Dispatch Safety Check/i });
    if (await validateBtn.isEnabled()) {
      await validateBtn.click();
      await expect(page.getByText(/Pre-dispatch Checks/i)).toBeVisible({ timeout: 5000 });
    }
  });

});
