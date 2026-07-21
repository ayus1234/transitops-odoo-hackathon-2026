from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    
    # Setup console and error listeners
    page.on("console", lambda msg: print(f"CONSOLE [{msg.type}]: {msg.text}"))
    page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
    
    # Get token via API login
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
    os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:1234@localhost:5432/transitops"
    os.environ["SECRET_KEY"] = "thisisasecretkeyforlocaldevelopmentonly123"
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.core.security import create_access_token
    from datetime import timedelta
    
    db = SessionLocal()
    user = db.query(User).filter(User.email.ilike('%admin%')).first()
    if user:
        token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(minutes=60))
        page.goto("http://localhost:5173/")
        page.evaluate(f"localStorage.setItem('token', '{token}')")
    else:
        print("No admin user found in DB!")
    
    print("Navigating to /inventory/restock...")
    page.goto("http://localhost:5173/inventory/restock")
    
    # Wait a bit for React to render and potentially crash
    time.sleep(5)
    
    print("Current URL:", page.url)
    
    print("Done waiting. Checking if element exists...")
    try:
        content = page.content()
        if "Inventory Dashboard" in content:
            print("Dashboard rendered successfully.")
            
            # Click the adjust stock button
            print("Clicking Adjust Stock...")
            page.click("button[title='Adjust Stock']")
            time.sleep(2)
            
            # Dump the modal HTML
            modal_html = page.evaluate("() => { const el = document.querySelector('.fixed.inset-0 > .bg-surface'); return el ? el.outerHTML : 'NOT FOUND'; }")
            print("MODAL CONTENT HTML:")
            print(modal_html)
            
            box = page.evaluate("() => { const el = document.querySelector('.fixed.inset-0 > .bg-surface'); if (!el) return null; const rect = el.getBoundingClientRect(); const style = window.getComputedStyle(el); return { rect: rect, opacity: style.opacity, display: style.display, visibility: style.visibility, zIndex: style.zIndex }; }")
            print("MODAL CONTENT CSS/BOX:", box)
            
            box2 = page.evaluate("() => { const el = document.querySelector('.fixed.inset-0'); if (!el) return null; const rect = el.getBoundingClientRect(); const style = window.getComputedStyle(el); return { rect: rect, opacity: style.opacity, display: style.display, visibility: style.visibility, zIndex: style.zIndex }; }")
            print("MODAL WRAPPER CSS/BOX:", box2)
            
        else:
            print("Dashboard NOT found in HTML. Blank screen confirmed.")
    except Exception as e:
        print("Error checking content:", e)
        
    try:
        body_text = page.inner_text("body")
        print("Body Text Preview:", body_text[:200])
    except Exception as e:
        print("Error getting body text:", e)
        
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
