"""
Verification Script: Lock Contention
Reason: Verify that AtomicLock correctly serializes access across processes.
"""
import sys
import os
import time
import multiprocessing
from utils.file_lock import AtomicLock

LOCK_FILE = "d:/iteration 3 framework/verify_lock.lock"
OUTPUT_FILE = "d:/iteration 3 framework/verify_output.txt"

def worker(worker_id):
    """
    Tries to acquire lock, write to file, wait, then release.
    """
    try:
        lock = AtomicLock(LOCK_FILE, timeout_seconds=20)
        with lock:
            print(f"Worker {worker_id} acquired lock.")
            # Critical Section
            with open(OUTPUT_FILE, "a") as f:
                f.write(f"Worker {worker_id} start\n")
            
            time.sleep(1) # simulate work
            
            with open(OUTPUT_FILE, "a") as f:
                f.write(f"Worker {worker_id} end\n")
            print(f"Worker {worker_id} released lock.")
            return True
    except Exception as e:
        print(f"Worker {worker_id} FAILED: {e}")
        return False

def test_lock_contention_verification():
    # Setup
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    processes = []
    
    # Spawn 5 concurrent workers
    print("Spawning 5 workers...")
    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(i,))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
        
    # Verify Content
    print("\\nVerifying output...")
    with open(OUTPUT_FILE, "r") as f:
        lines = f.readlines()
        
    # Validation Rule: "start" and "end" must be interleaved perfectly for a single worker
    # because the lock should prevent overlap.
    # Pattern must be: start, end, start, end...
    
    is_valid = True
    active_worker = None
    
    for line in lines:
        parts = line.strip().split() # ["Worker", "0", "start"]
        w_id = parts[1]
        action = parts[2]
        
        if action == "start":
            if active_worker is not None:
                print(f"ERROR: Worker {w_id} started while Worker {active_worker} was running!")
                is_valid = False
            active_worker = w_id
        elif action == "end":
            if active_worker != w_id:
                 print(f"ERROR: Worker {w_id} ended but {active_worker} was supposed to be running!")
                 is_valid = False
            active_worker = None
            
    if is_valid and len(lines) == 10:
        print("SUCCESS: Lock enforced perfect serialization.")
        # Cleanup
        if os.path.exists(OUTPUT_FILE):
             os.remove(OUTPUT_FILE)
        if os.path.exists(LOCK_FILE):
             try:
                os.remove(LOCK_FILE)
             except OSError:
                pass
        assert True
    else:
        print("FAILURE: Trace shows race conditions.")
        print("".join(lines))
        assert False, "Lock contention verification failed"

if __name__ == "__main__":
    # Add root to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_verification()
