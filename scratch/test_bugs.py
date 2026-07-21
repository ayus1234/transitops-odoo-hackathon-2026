from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()

    # Capture console messages
    page.on("console", lambda msg: print(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[PageError] {err}"))

    print("Navigating to Inventory...")
    try:
        page.goto("http://localhost:5173/inventory/restock", timeout=5000, wait_until="networkidle")
    except Exception as e:
        print(f"Inventory nav error: {e}")

    print("Navigating to Reports...")
    try:
        page.goto("http://localhost:5173/reports", timeout=5000, wait_until="networkidle")
    except Exception as e:
        print(f"Reports nav error: {e}")

    print("Navigating to License Compliance...")
    try:
        page.goto("http://localhost:5173/drivers/license-compliance", timeout=5000, wait_until="networkidle")
    except Exception as e:
        print(f"License nav error: {e}")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
