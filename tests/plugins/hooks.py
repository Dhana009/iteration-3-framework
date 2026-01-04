def pytest_sessionstart(session):
    """
    Morning Roll Call: Reset User State on Session Start.
    Runs ONLY on the Master node (before workers start).
    Ensures recovery from previous crashes by clearing the state file.
    """
    if not hasattr(session.config, 'workerinput'):
        # Inline imports for safety
        import json
        from pathlib import Path
        from utils.file_lock import AtomicLock
        
        # Robust path resolution using pytest's rootdir
        root = Path(session.config.rootdir)
        state_path = root / 'config' / 'user_state.json'
        lock_path = root / 'config' / 'user_pool.lock'
        
        try:
            # We blindly reset state to {} because this is a FRESH session.
            # No tests are running yet, so no valid locks exist.
            with AtomicLock(lock_path, timeout_seconds=10):
                with open(state_path, 'w') as f:
                    json.dump({}, f)
                print(f"[Morning Roll Call] Reset user state at {state_path}")
                
        except Exception as e:
            print(f"[Morning Roll Call] Error: {e}")
