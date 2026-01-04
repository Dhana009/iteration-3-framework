from pathlib import Path
from playwright.sync_api import Browser, Page
from lib.pages.login_page import LoginPage

# ROOT_DIR is calculated relative to this file (d:/.../lib/ui_auth.py)
# Parent is 'lib', Parent.Parent is 'root'
ROOT_DIR = Path(__file__).parent.parent
STATE_DIR = ROOT_DIR / 'state'

class SmartUIAuth:
    """
    Traffic Control for UI Sessions (Storage State).
    Logic:
    1. Check if valid storage_state exists for user.
    2. If yes -> Return path (Reuse).
    3. If no -> Perform UI Login -> Save State -> Return path.
    """
    def __init__(self, email, password, browser: Browser, base_url: str):
        self.email = email
        self.password = password
        self.browser = browser
        self.base_url = base_url.rstrip('/') # Validate format
        self.state_path = STATE_DIR / f"{self.email}_storage.json"
        
        if not STATE_DIR.exists():
            STATE_DIR.mkdir(parents=True, exist_ok=True)

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
        Validates state by attempting to use it.
        Creates a test context and checks if we're still authenticated.
        Similar to SmartAuth's token validation approach.
        """
        if not self.state_path.exists():
            return False
        
        try:
            # Create a test context with the state
            context = self.browser.new_context(storage_state=str(self.state_path), base_url=self.base_url)
            page = context.new_page()
            
            # Try to navigate to a protected page (dashboard is typically protected)
            # Using a short timeout to fail fast if state is invalid
            page.goto(f"{self.base_url}/dashboard", wait_until="domcontentloaded", timeout=5000)
            
            # Check if we're redirected to login (means invalid state)
            current_url = page.url
            is_valid = "/login" not in current_url.lower()
            
            context.close()
            
            if not is_valid:
                print(f"[SmartUIAuth] State for {self.email} is EXPIRED (redirected to login)")
                # Clean up expired state
                self.state_path.unlink()
            
            return is_valid
            
        except Exception as e:
            # Any error means state is invalid (network issues, timeout, etc.)
            print(f"[SmartUIAuth] State validation failed for {self.email}: {e}")
            if self.state_path.exists():
                self.state_path.unlink()
            return False

    def _login_and_save(self):
        """
        Performs the physical UI login and saves storage state.
        Uses POM (LoginPage) for maintainability.
        """
        page = self.browser.new_page()
        try:
            print(f"[SmartUIAuth] Navigating to Login...")
            login_page = LoginPage(page)
            
            # Using POM methods
            login_page.navigate(self.base_url)
            login_page.login(self.email, self.password)
            login_page.wait_for_success()
            
            # Save State
            page.context.storage_state(path=self.state_path)
            print(f"[SmartUIAuth] Session saved to {self.state_path}")
            
        except Exception as e:
            print(f"[SmartUIAuth] Login Failed: {e}")
            # Ensure we don't save broken state
            if self.state_path.exists():
                self.state_path.unlink()
            raise e
        finally:
            page.close()
