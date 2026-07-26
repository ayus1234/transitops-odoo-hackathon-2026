import { test, expect } from '@playwright/test';

test.describe('Demo Login Accounts and Password Visibility Controls', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('Password visibility eye button toggles input type without clearing value', async ({ page }) => {
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

  test('Demo Accounts section expands and Use Account populates credentials cleanly', async ({ page }) => {
    // Check demo section title exists when VITE_DEMO_MODE=true
    const viewDemoBtn = page.locator('button', { hasText: /View Demo Accounts/i });
    await expect(viewDemoBtn).toBeVisible();

    // Click to expand Demo Accounts panel
    await viewDemoBtn.click();

    // Verify all 9 configured roles are listed
    const roles = [
      'Super Admin',
      'Administrator',
      'Fleet Manager',
      'Dispatcher',
      'Maintenance Manager',
      'Technician',
      'Safety Officer',
      'HR/Operations',
      'Driver'
    ];
    for (const role of roles) {
      await expect(page.locator('span', { hasText: role }).first()).toBeVisible();
    }

    // Click Use Account for Fleet Manager
    const fleetCard = page.locator('div').filter({ hasText: 'Fleet Manager' }).filter({ hasText: 'fleet@transitops.com' }).first();
    const useAccountBtn = fleetCard.locator('button', { hasText: /Use Account/i });
    await useAccountBtn.click();

    // Verify Email and Password input fields are populated with Fleet Manager credentials
    await expect(page.locator('input#email')).toHaveValue('fleet@transitops.com');
    await expect(page.locator('input#password')).toHaveValue('fleet2026');

    // Verify user is NOT automatically logged in (login form still present)
    await expect(page.locator('button[type="submit"]', { hasText: /Sign In/i })).toBeVisible();

    // Click Use Account for Dispatcher to ensure account A never bleeds into account B
    const dispatcherCard = page.locator('div').filter({ hasText: 'Dispatcher' }).filter({ hasText: 'dispatcher@transitops.com' }).first();
    await dispatcherCard.locator('button', { hasText: /Use Account/i }).click();
    await expect(page.locator('input#email')).toHaveValue('dispatcher@transitops.com');
    await expect(page.locator('input#password')).toHaveValue('dispatch2026');
  });

  test('Demo password individual visibility toggle in account cards', async ({ page }) => {
    await page.locator('button', { hasText: /View Demo Accounts/i }).click();
    
    // Default displayed password should be ••••••••
    const adminCard = page.locator('div').filter({ hasText: 'Super Admin' }).filter({ hasText: 'admin@transitops.com' }).first();
    await expect(adminCard.locator('span', { hasText: '••••••••' })).toBeVisible();

    // Click toggle button for Super Admin demo password
    const showDemoPassBtn = adminCard.locator('button[aria-label="Show Super Admin demo password"]');
    await showDemoPassBtn.click();

    // Password becomes actual demo password
    await expect(adminCard.locator('span', { hasText: 'admin123' })).toBeVisible();

    // Hide it again
    await adminCard.locator('button[aria-label="Hide Super Admin demo password"]').click();
    await expect(adminCard.locator('span', { hasText: '••••••••' })).toBeVisible();
  });
});
