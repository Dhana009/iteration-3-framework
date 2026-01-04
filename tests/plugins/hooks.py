def pytest_sessionstart(session):
    """
    Morning Roll Call: Reset User Pool on Session Start.
    Runs ONLY on the Master node (before workers start).
    Ensures recovery from previous crashes by un-reserving all users.
    """
    if not hasattr(session.config, 'workerinput'):
        # Inline imports for safety
        import json
        from pathlib import Path
        from utils.file_lock import AtomicLock
        
        # Robust path resolution using pytest's rootdir
        root = Path(session.config.rootdir)
        config_path = root / 'config' / 'user_pool.json'
        # AtomicLock expects Union[str, Path], so we can pass Path directly now
        lock_path = root / 'config' / 'user_pool.lock'
        
        if not config_path.exists():
            print(f"[Morning Roll Call] Config not found at {config_path}")
            return
        
        try:
            with AtomicLock(lock_path, timeout_seconds=10):
                with open(config_path, 'r+') as f:
                    pool = json.load(f)
                    reset_count = 0
                    
                    for role in pool:
                        for user in pool[role]:
                            if user.get('reserved_by'):
                                user['reserved_by'] = None
                                reset_count += 1
                    
                    if reset_count > 0:
                        f.seek(0)
                        json.dump(pool, f, indent=4)
                        f.truncate()
                        print(f"[Morning Roll Call] Released {reset_count} stuck users.")
                    else:
                        print("[Morning Roll Call] User pool is clean.")
        except Exception as e:
            print(f"[Morning Roll Call] Error: {e}")
