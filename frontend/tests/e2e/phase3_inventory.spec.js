import { test, expect } from '@playwright/test';

test.describe('Phase 3 - Inventory & Procurement', () => {
  let authToken;
  let partId;
  let reqId;
  let poNumber;

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

  test('Inventory Workflow: Create Request -> Approve -> Generate PO -> Deliver -> Restock', async ({ page, request }) => {
    // ----------------------------------------------------
    // 1. Create Procurement Request
    // ----------------------------------------------------
    page.on('response', async response => {
      if (!response.ok() && response.url().includes('/api/v1/procurement/requests')) {
        console.error('API Error:', await response.text());
      }
    });

    await page.goto('http://localhost:5173/inventory/procurement');
    
    // Click New Request
    await page.locator('button:has-text("New Request")').click();
    await expect(page.locator('h2').filter({ hasText: 'New Procurement Request' })).toBeVisible({ timeout: 5000 });

    const modal = page.locator('.fixed').filter({ hasText: 'New Procurement Request' });

    // We will just select the first available part
    const partSelect = modal.locator('select').first();
    await partSelect.selectOption({ index: 1 }); 
    partId = await partSelect.inputValue(); // Get the ID of the selected part
    
    await modal.locator('input[type="number"]').nth(0).fill('10');
    await modal.locator('input[type="number"]').nth(2).fill('250.00');
    await modal.getByPlaceholder('Preferred Vendor').fill('Test Vendor Inc.');
    await modal.locator('select').nth(1).selectOption('High');
    
    await modal.locator('button:has-text("Create Request")').click();
    await expect(page.locator('h2').filter({ hasText: 'New Procurement Request' })).not.toBeVisible({ timeout: 8000 });

    // Find the row by Vendor Name
    const requestRow = page.locator('tr').filter({ hasText: 'Test Vendor Inc.' }).first();
    await expect(requestRow).toBeVisible({ timeout: 5000 });

    // Get Request ID from the first column
    const reqIdText = await requestRow.locator('td').first().innerText();
    
    // The backend uses UUIDs, the frontend displays the first 8 chars, or the `id`. We'll fetch it from the API to be safe.
    const requestsResponse = await request.get('http://127.0.0.1:8000/api/v1/procurement/requests?page_size=10', {
      headers: { Authorization: `Bearer ${authToken}` }
    });
    const requestsData = await requestsResponse.json();
    const createdReq = requestsData.data.find(r => r.vendor === 'Test Vendor Inc.' && r.status === 'Submitted');
    reqId = createdReq.id;

    // ----------------------------------------------------
    // 2. Approve Procurement Request
    // ----------------------------------------------------
    await requestRow.locator('button[title="Approve"]').click();
    await expect(requestRow.locator('span:has-text("APPROVED")')).toBeVisible({ timeout: 5000 });

    // ----------------------------------------------------
    // 3. Generate Purchase Order (Simulating backend trigger)
    // ----------------------------------------------------
    const poResponse = await request.post(`http://127.0.0.1:8000/api/v1/purchase-orders/generate/${reqId}`, {
      headers: { Authorization: `Bearer ${authToken}` }
    });
    expect(poResponse.ok()).toBeTruthy();
    const poData = await poResponse.json();
    poNumber = poData.data.po_number;

    // ----------------------------------------------------
    // 4. Update PO Status to Delivered
    // ----------------------------------------------------
    await page.goto('http://localhost:5173/inventory/purchase-orders');
    
    // Wait for the table to load
    const poRow = page.locator('tr').filter({ hasText: poNumber }).first();
    await expect(poRow).toBeVisible({ timeout: 5000 });

    // Open Status Modal
    await poRow.locator('button[title="Update Status"]').click();
    await expect(page.locator('h2').filter({ hasText: 'Update PO Status' })).toBeVisible({ timeout: 5000 });

    // Change status to Delivered
    await page.locator('.fixed select').selectOption('Delivered');
    await page.locator('.fixed button:has-text("Confirm")').click();
    await expect(page.locator('h2').filter({ hasText: 'Update PO Status' })).not.toBeVisible({ timeout: 8000 });

    // Verify it is Delivered
    await expect(poRow.locator('span:has-text("DELIVERED")')).toBeVisible({ timeout: 5000 });

    // ----------------------------------------------------
    // 5. Verify Inventory History (Restock)
    // ----------------------------------------------------
    await page.goto('http://localhost:5173/inventory/history');
    
    // Should see a RESTOCK entry with the PO Number in reference_id
    const historyRow = page.locator('tr').filter({ hasText: poNumber }).first();
    await expect(historyRow).toBeVisible({ timeout: 5000 });
    
    // Make sure it says RESTOCK
    await expect(historyRow.locator('td', { hasText: 'RESTOCK' }).first()).toBeVisible();
    
    // Make sure quantity increased by 10
    await expect(historyRow.locator('td', { hasText: '+10' }).first()).toBeVisible();
  });
});
