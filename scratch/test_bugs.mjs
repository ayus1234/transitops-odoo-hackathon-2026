import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`[Browser Error]: ${msg.text()}`);
    }
  });

  page.on('pageerror', error => {
    console.log(`[Page Error]: ${error.message}`);
  });

  try {
    console.log("Navigating to Inventory...");
    await page.goto('http://localhost:5173/inventory', { waitUntil: 'networkidle', timeout: 5000 });
  } catch (e) {
    console.log(`Inventory navigation error: ${e.message}`);
  }

  try {
    console.log("Navigating to Reports...");
    await page.goto('http://localhost:5173/reports', { waitUntil: 'networkidle', timeout: 5000 });
  } catch (e) {
    console.log(`Reports navigation error: ${e.message}`);
  }

  try {
    console.log("Navigating to License Compliance...");
    await page.goto('http://localhost:5173/drivers/compliance', { waitUntil: 'networkidle', timeout: 5000 });
  } catch (e) {
    console.log(`License navigation error: ${e.message}`);
  }

  await browser.close();
})();
