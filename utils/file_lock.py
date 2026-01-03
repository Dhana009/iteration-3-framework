"""
Atomic File Locking Utility
Reason: We need a reliable way to synchronize access to shared resources (user pool, seed data) across parallel processes.
Standard `filelock` is good, but we wrap it to enforce our specific timeout logic (Fail Fast).
"""

import os
import time
from filelock import FileLock, Timeout

class AtomicLock:
    def __init__(self, lock_file_path: str, timeout_seconds: int = 10):
        """
        Initialize the lock.
        :param lock_file_path: Absolute path to the lock file.
        :param timeout_seconds: How long to wait before crashing. 
                                We deliberately keep this short. If we wait >10s, something is wrong.
        """
        self.lock_file = lock_file_path
        self.timeout = timeout_seconds
        self.lock = FileLock(lock_file_path, timeout=timeout_seconds)

    def acquire(self):
        """
        Acquire the lock. Raises Timeout if acquisition fails.
        """
        try:
            self.lock.acquire()
        except Timeout:
            raise TimeoutError(f"CRITICAL: Failed to acquire lock {self.lock_file} after {self.timeout}s. System is congested or deadlocked.")

    def release(self):
        """
        Release the lock.
        """
        self.lock.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
