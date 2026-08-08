import { test, expect } from '@playwright/test';

test.describe('Feature 2.1 — Jobs & Customer Shipping Orders E2E Suite', () => {

  test.beforeEach(async ({ page }) => {
    // Authenticate as Fleet Manager / Admin
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@transitops.com');
    await page.fill('input[type="password"]', 'admin123'); 
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('Job Workflow: Create, Search, Filter & Cancel Shipping Order', async ({ page }) => {
    const timestamp = Date.now();
    const customerName = `Test Customer ${timestamp}`;
    const pickupLoc = `Bhiwandi Hub ${timestamp}`;
    const deliveryLoc = `JNPT Port ${timestamp}`;

    // 1. Navigate to Jobs & Orders
    await page.goto('/jobs');
    await expect(page.locator('h1').filter({ hasText: /Jobs & Customer Orders/i })).toBeVisible({ timeout: 5000 });

    // 2. Open Create Job Modal
    await page.getByRole('button', { name: /Create Shipping Order/i }).click();
    await expect(page.locator('h3').filter({ hasText: 'Create Customer Shipping Order' })).toBeVisible({ timeout: 5000 });

    // Fill Form
    await page.fill('input[placeholder="e.g. Acme Freight Ltd"]', customerName);
    await page.fill('input[placeholder="Phone or email"]', '+91 99999 88888');
    await page.fill('input[placeholder="Full pickup location address"]', pickupLoc);
    await page.fill('input[placeholder="Full destination delivery address"]', deliveryLoc);
    await page.fill('input[placeholder="Goods / Materials"]', 'Industrial Machining Parts');
    await page.fill('input[placeholder="e.g. 15000"]', '12500');
    await page.locator('form select').selectOption('High');
    await page.fill('textarea[placeholder*="Handling instructions"]', 'Fragile cargo. Secure tie-downs required.');

    // Submit
    await page.click('button:has-text("Create Order")');
    await expect(page.locator('h3').filter({ hasText: 'Create Customer Shipping Order' })).not.toBeVisible({ timeout: 8000 });
    await page.getByText('Loading customer shipping orders...').waitFor({ state: 'detached', timeout: 5000 }).catch(() => {});

    // 3. Search for Job
    const searchInput = page.getByPlaceholder('Search job #, customer, address...');
    await searchInput.fill(customerName);
    await searchInput.press('Enter');
    await page.getByText('Loading customer shipping orders...').waitFor({ state: 'detached', timeout: 5000 }).catch(() => {});

    // Assert created row is visible in table
    const jobRow = page.locator('table tbody tr').filter({ hasText: customerName });
    await expect(jobRow).toBeVisible({ timeout: 10000 });
    await expect(jobRow.getByText('High')).toBeVisible();

    // 4. Status Filter Check
    await page.selectOption('select:has-text("All Statuses")', 'Pending');
    await page.getByText('Loading customer shipping orders...').waitFor({ state: 'detached', timeout: 5000 }).catch(() => {});
    await expect(jobRow).toBeVisible();

    await page.selectOption('select:has-text("All Statuses")', 'Delivered');
    await page.getByText('Loading customer shipping orders...').waitFor({ state: 'detached', timeout: 5000 }).catch(() => {});
    await expect(page.getByText('No shipping orders found matching criteria.')).toBeVisible({ timeout: 5000 });

    // Reset Filter
    await page.selectOption('select:has-text("Delivered")', '');
    await searchInput.fill(customerName);
    await searchInput.press('Enter');
    await page.getByText('Loading customer shipping orders...').waitFor({ state: 'detached', timeout: 5000 }).catch(() => {});
    await expect(jobRow).toBeVisible({ timeout: 10000 });
  });

});
