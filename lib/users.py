import json
from pathlib import Path
import pytest
from utils.file_lock import AtomicLock

CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'user_pool.json'
LOCK_PATH = Path(__file__).parent.parent / 'config' / 'user_pool.lock'

class UserLease:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.user = None

    def acquire(self, role: str):
        """
        Acquire a user of the given role.
        CRITICAL: Fails immediately if no user is available.
        """
        print(f"[{self.worker_id}] Attempting to lease {role}...")
        
        # 1. Atomic Lock
        with AtomicLock(LOCK_PATH, timeout_seconds=10):
            # 2. Read Pool
            with open(CONFIG_PATH, 'r+') as f:
                pool = json.load(f)
                
                # 3. Find Free User
                candidate = None
                users = pool.get(role, [])
                
                for u in users:
                    # check if 'reserved_by' key exists and is None/Empty
                    if not u.get('reserved_by'):
                        candidate = u
                        break
                
                # 4. Fail Fast
                if not candidate:
                    raise RuntimeError(f"INFRASTRUCTURE_ERROR: No free users available for role '{role}'. Pool exhausted.")
                
                # 5. Mark Busy
                candidate['reserved_by'] = self.worker_id
                self.user = candidate
                
                # 6. Write Back
                f.seek(0)
                json.dump(pool, f, indent=4)
                f.truncate()
                
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
             with open(CONFIG_PATH, 'r+') as f:
                pool = json.load(f)
                
                # Find and clear
                found = False
                for role in pool:
                    for u in pool[role]:
                        if u['email'] == self.user['email']:
                            u['reserved_by'] = None
                            found = True
                            break
                    if found: break
                
                f.seek(0)
                json.dump(pool, f, indent=4)
                f.truncate()
        self.user = None

@pytest.fixture
def user_lease(worker_id):
    """
    Fixture that yields a UserLease object.
    Automatically handles release on teardown.
    """
    lease = UserLease(worker_id)
    yield lease
    lease.release()
