"""
Thread-safe Singleton metaclass.

Ensures only one instance of a class exists across application lifecycle.
"""

import threading
from typing import Dict, Any


class SingletonMeta(type):
    """
    Thread-safe Singleton metaclass.
    
    Usage:
        class MyService(metaclass=SingletonMeta):
            def __init__(self, config):
                self.config = config
    
    This ensures only one instance exists, even in multi-threaded environments.
    """
    
    _instances: Dict[type, Any] = {}
    _lock: threading.Lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        """
        Control instance creation.
        
        Thread-safe implementation using double-checked locking pattern.
        """
        # First check (without lock) for performance
        if cls not in cls._instances:
            # Acquire lock only if instance doesn't exist
            with cls._lock:
                # Second check (with lock) to prevent race condition
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        
        return cls._instances[cls]

