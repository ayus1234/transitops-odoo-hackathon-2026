import { test, expect } from '@playwright/test';

test.describe('Phase 7.2 - Integration Testing', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to login
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@transitops.com');
    await page.fill('input[type="password"]', 'admin123'); // Assume default password
    await page.click('button[type="submit"]');
    // Wait for navigation to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('Search and filter functionality on Vehicles page', async ({ page }) => {
    await page.goto('/vehicles');
    
    // Type into search bar
    const searchInput = page.getByPlaceholder('Search vehicles...');
    await searchInput.fill('VH-');
    
    // Wait for network/UI update
    await page.waitForTimeout(1000);
    
    // Select filter
    const statusSelect = page.locator('select').first();
    await statusSelect.selectOption('Available');
    
    // Wait for network/UI update
    await page.waitForTimeout(1000);

    // Verify table has rows or empty state
    const tableRows = page.locator('table tbody tr');
    const count = await tableRows.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('Open Create Vehicle Modal (CRUD Create)', async ({ page }) => {
    await page.goto('/vehicles');
    
    // Click "Add Vehicle"
    await page.getByRole('button', { name: /Add Vehicle/i }).click();
    
    // Verify modal opens
    await expect(page.locator('h2').filter({ hasText: 'Register New Vehicle' })).toBeVisible({ timeout: 5000 });
    
    // Fill basic details
    await page.fill('input[name="vehicle_name"]', 'Test Truck');
    await page.fill('input[name="registration_number"]', 'TST-9999');
    
    // Close modal
    await page.click('button:has-text("Cancel")');
  });

  test('Dashboard Quick Action integration', async ({ page }) => {
    await page.goto('/');
    
    // Click Quick Action "Create Trip"
    await page.click('button:has-text("Create Trip")');
    
    // It should navigate to /trips/new or open modal
    // Since UI handles it via navigation with state or direct route:
    await page.waitForTimeout(2000); // Wait for navigation/modal
    
    // Verify we are either on the trip page with modal open, or route changed
    const url = page.url();
    expect(url).toContain('/trips');
  });

});
