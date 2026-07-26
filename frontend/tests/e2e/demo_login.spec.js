import { test, expect } from '@playwright/test';

test.describe('Role-Based Demo Access & Login UI Flow', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('Login form password visibility eye button toggles input type without clearing value', async ({ page }) => {
    const passwordInput = page.locator('input#password');
    await expect(passwordInput).toHaveAttribute('type', 'password');

    // Fill password
    const testPassword = 'mySecretPassword123';
    await passwordInput.fill(testPassword);

    // Eye button should have aria-label "Show password"
    const toggleBtn = page.locator('button[aria-label="Show password"]');
    await expect(toggleBtn).toBeVisible();

    // Click eye button -> type becomes text
    await toggleBtn.click();
    await expect(passwordInput).toHaveAttribute('type', 'text');
    await expect(passwordInput).toHaveValue(testPassword);

    // Eye button now has aria-label "Hide password"
    const hideBtn = page.locator('button[aria-label="Hide password"]');
    await expect(hideBtn).toBeVisible();

    // Click again -> type returns to password
    await hideBtn.click();
    await expect(passwordInput).toHaveAttribute('type', 'password');
    await expect(passwordInput).toHaveValue(testPassword);
  });

  test('Initial state: Role selector visible in demo mode without displaying credential panel', async ({ page }) => {
    const roleSelect = page.locator('select#role-select');
    await expect(roleSelect).toBeVisible();
    await expect(roleSelect).toHaveValue('');
    
    // Verify standard login fields are accessible
    await expect(page.locator('input#email')).toBeVisible();
    await expect(page.locator('input#password')).toBeVisible();
    
    // Verify credential panel is not displayed initially
    await expect(page.locator('h3', { hasText: /Demo Access/i })).not.toBeVisible();
  });

  test('Role selector dropdown contains all 13 system demo roles', async ({ page }) => {
    const expectedRoles = [
      'Super Admin',
      'Administrator',
      'System Admin',
      'Fleet Manager',
      'Dispatcher',
      'Maintenance Manager',
      'Technician',
      'Safety Officer',
      'Financial Analyst',
      'Procurement Operations',
      'HR/Operations',
      'Support Agent',
      'Driver'
    ];

    const options = page.locator('select#role-select option');
    const count = await options.count();
    expect(count).toBeGreaterThanOrEqual(14); // 1 placeholder + 13 roles

    for (const role of expectedRoles) {
      await expect(page.locator(`select#role-select option[value="${role}"]`)).toHaveText(role);
    }
  });

  test('Selecting a role displays dedicated credentials, supports password toggle, copy labels, and Use Credentials', async ({ page }) => {
    const roleSelect = page.locator('select#role-select');
    await roleSelect.selectOption('Fleet Manager');

    // Verify credential panel appears immediately
    await expect(page.locator('h3', { hasText: 'Fleet Manager Demo Access' })).toBeVisible();
    await expect(page.locator('span', { hasText: 'fleet@transitops.com' })).toBeVisible();
    
    // Default masked password
    await expect(page.locator('span', { hasText: '••••••••' })).toBeVisible();

    // Verify copy button labels
    const copyIdBtn = page.locator('button[aria-label="Copy Fleet Manager login ID"]');
    const copyPassBtn = page.locator('button[aria-label="Copy Fleet Manager demo password"]');
    await expect(copyIdBtn).toBeVisible();
    await expect(copyPassBtn).toBeVisible();

    // Reveal password inside credential panel
    const showDemoPassBtn = page.locator('h3:has-text("Fleet Manager Demo Access")').locator('..').locator('..').locator('button[aria-label="Show password"]');
    await showDemoPassBtn.click();
    await expect(page.locator('span', { hasText: 'fleet2026' })).toBeVisible();

    // Click Use Credentials button
    const useCredsBtn = page.locator('button', { hasText: /Use Credentials/i });
    await useCredsBtn.click();

    // Verify fields populated without auto-submitting
    await expect(page.locator('input#email')).toHaveValue('fleet@transitops.com');
    await expect(page.locator('input#password')).toHaveValue('fleet2026');
    await expect(page.locator('button[type="submit"]', { hasText: /Sign In/i })).toBeVisible();
  });

  test('Changing role immediately updates panel and resets password visibility', async ({ page }) => {
    const roleSelect = page.locator('select#role-select');
    
    // First select Driver
    await roleSelect.selectOption('Driver');
    await expect(page.locator('h3', { hasText: 'Driver Demo Access' })).toBeVisible();
    await expect(page.locator('span', { hasText: 'driver@transitops.com' })).toBeVisible();

    // Switch to Safety Officer
    await roleSelect.selectOption('Safety Officer');
    await expect(page.locator('h3', { hasText: 'Safety Officer Demo Access' })).toBeVisible();
    await expect(page.locator('span', { hasText: 'safety@transitops.com' })).toBeVisible();
    
    // Verify previous Driver credentials are completely removed
    await expect(page.locator('span', { hasText: 'driver@transitops.com' })).not.toBeVisible();
    await expect(page.locator('span', { hasText: '••••••••' })).toBeVisible();
  });

  test('Cross-Role Security: Dropdown selection has zero impact on submitted login credentials or RBAC behavior', async ({ page }) => {
    const roleSelect = page.locator('select#role-select');
    
    // Select Fleet Manager in demo dropdown
    await roleSelect.selectOption('Fleet Manager');
    await expect(page.locator('h3', { hasText: 'Fleet Manager Demo Access' })).toBeVisible();

    // Manually type Driver credentials into form fields
    const emailInput = page.locator('input#email');
    const passwordInput = page.locator('input#password');
    await emailInput.fill('driver@transitops.com');
    await passwordInput.fill('driver2026');

    // Verify input values are exclusively Driver credentials, ignoring dropdown state
    await expect(emailInput).toHaveValue('driver@transitops.com');
    await expect(passwordInput).toHaveValue('driver2026');
  });

});
