import os
import time
from playwright.sync_api import Browser, Page

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(ROOT_DIR, 'state')

class SmartUIAuth:
    """
    Traffic Control for UI Sessions (Storage State).
    Logic:
    1. Check if valid storage_state exists for user.
    2. If yes -> Return path (Reuse).
    3. If no -> Perform UI Login -> Save State -> Return path.
    """
    def __init__(self, email, password, browser: Browser):
        self.email = email
        self.password = password
        self.browser = browser
        self.state_path = os.path.join(STATE_DIR, f"{email}_storage.json")
        
        if not os.path.exists(STATE_DIR):
            os.makedirs(STATE_DIR)

    def get_storage_state(self):
        """
        Returns the path to a valid storage state file.
        Lazily creates it if missing.
        """
        if self._is_state_valid():
            print(f"[SmartUIAuth] Reusing session for {self.email}")
            return self.state_path
        
        print(f"[SmartUIAuth] No valid session for {self.email}. Logging in...")
        self._login_and_save()
        return self.state_path

    def _is_state_valid(self):
        """
        Checks if state file exists.
        Future: Could load it and check expiry timestamp.
        """
        return os.path.exists(self.state_path)

    def _login_and_save(self):
        """
        Performs the physical UI login and saves storage state.
        """
        page = self.browser.new_page()
        try:
            print(f"[SmartUIAuth] Navigating to Login...")
            page.goto("https://testing-box.vercel.app/login")
            
            # Use verified selectors
            page.fill('[data-testid="login-email"]', self.email)
            page.fill('[data-testid="login-password"]', self.password)
            page.click('[data-testid="login-submit"]')
            
            # Wait for success (Dashboard)
            page.wait_for_url("**/dashboard", timeout=15000)
            
            # Save State
            page.context.storage_state(path=self.state_path)
            print(f"[SmartUIAuth] Session saved to {self.state_path}")
            
        except Exception as e:
            print(f"[SmartUIAuth] Login Failed: {e}")
            # Ensure we don't save broken state
            if os.path.exists(self.state_path):
                os.remove(self.state_path)
            raise e
        finally:
            page.close()
