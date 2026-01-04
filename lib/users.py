import json
from pathlib import Path
import pytest
from utils.file_lock import AtomicLock

CONFIG_DIR = Path(__file__).parent.parent / 'config'
CONFIG_PATH = CONFIG_DIR / 'user_pool.json'
STATE_PATH = CONFIG_DIR / 'user_state.json'
LOCK_PATH = CONFIG_DIR / 'user_pool.lock'

class UserLease:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.user = None
        self.role = None
        
        # Ensure state file exists (Lazy Init)
        if not STATE_PATH.exists():
            # Use lock to avoid race on creation
            with AtomicLock(LOCK_PATH, timeout_seconds=5):
                if not STATE_PATH.exists():
                    with open(STATE_PATH, 'w') as f:
                        json.dump({}, f)

    def acquire(self, role: str):
        """
        Acquire a user of the given role.
        CRITICAL: Fails immediately if no user is available.
        Optimization: Reads Config (Static) first, then Locks State (Dynamic).
        """
        print(f"[{self.worker_id}] Attempting to lease {role}...")
        
        # 1. Load Config (No Lock needed for static/setup-time config)
        try:
            with open(CONFIG_PATH, 'r') as f:
                pool_config = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load user config: {e}")
            
        candidates = pool_config.get(role, [])
        if not candidates:
             raise RuntimeError(f"INFRASTRUCTURE_ERROR: No users configured for role '{role}'.")

        # 2. Access State (Locked Critical Section)
        with AtomicLock(LOCK_PATH, timeout_seconds=10):
            # Load Current Reservations
            current_state = {}
            if STATE_PATH.exists():
                try:
                    with open(STATE_PATH, 'r') as f:
                        current_state = json.load(f) or {}
                except (json.JSONDecodeError, FileNotFoundError):
                    current_state = {} # Auto-heal corrupt state
            
            # Find Free User
            selected_user = None
            for user in candidates:
                email = user['email']
                if email not in current_state:
                    selected_user = user
                    break
            
            # 3. Fail Fast if Exhausted
            if not selected_user:
                 raise RuntimeError(f"INFRASTRUCTURE_ERROR: No free users available for role '{role}'. Pool exhausted.")
            
            # 4. Update State
            current_state[selected_user['email']] = self.worker_id
            
            with open(STATE_PATH, 'w') as f:
                json.dump(current_state, f, indent=4)
                
            self.user = selected_user
            self.role = role
            
        print(f"[{self.worker_id}] Leased {self.user['email']}")
        return self.user

    def release(self):
        """
        Release the user back to the pool.
        """
        if not self.user:
            return

        print(f"[{self.worker_id}] Releasing {self.user['email']}...")
        
        with AtomicLock(LOCK_PATH, timeout_seconds=10):
             # Load State
            current_state = {}
            if STATE_PATH.exists():
                try:
                    with open(STATE_PATH, 'r') as f:
                        current_state = json.load(f) or {}
                except json.JSONDecodeError:
                    current_state = {}

            # Remove Reservation
            email = self.user['email']
            if email in current_state:
                # We simply remove the key. 
                # (Optional future safety: verify worker_id matches)
                del current_state[email]
            
            # Save State
            with open(STATE_PATH, 'w') as f:
                json.dump(current_state, f, indent=4)

        self.user = None
        self.role = None

@pytest.fixture
def user_lease(worker_id):
    """
    Fixture that yields a UserLease object.
    Automatically handles release on teardown.
    """
    lease = UserLease(worker_id)
    yield lease
    lease.release()
