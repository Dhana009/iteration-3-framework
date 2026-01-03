from playwright.sync_api import sync_playwright
import time

def debug_login():
    with sync_playwright() as p:
        # Launch headed to see it, but also take screenshot
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        print("1. Navigating to Login...")
        page.goto("https://testing-box.vercel.app/login")
        
        print("2. Filling Credentials...")
        page.fill('[data-testid="login-email"]', "admin1@test.com")
        page.fill('[data-testid="login-password"]', "Test123!@#")
        
        print("3. Clicking Submit...")
        page.click('[data-testid="login-submit"]')
        
        print("4. Waiting for Redirect (10s)...")
        try:
            page.wait_for_url("**/items", timeout=10000)
            print("SUCCESS: Redirected to /items")
        except Exception as e:
            print(f"FAILURE: Stayed on {page.url}")
            page.screenshot(path="login_debug_fail.png")
            print("Screenshot saved to login_debug_fail.png")
            
            # Check for error message
            try:
                err = page.locator(".text-red-500").text_content() # Guessing Tailwind error class
                print(f"Visible Error: {err}")
            except:
                pass
                
        browser.close()

if __name__ == "__main__":
    debug_login()
