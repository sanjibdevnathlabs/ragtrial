"""
Thread-safe Singleton metaclass.

Ensures only one instance of a class exists across application lifecycle.
"""

import threading
from typing import Any, Dict


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
    _locks: Dict[type, threading.Lock] = {}
    _meta_lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """
        Control instance creation.

        Thread-safe implementation using double-checked locking pattern.
        Each class gets its own lock to prevent deadlocks when singletons
        create other singletons.
        """
        # First check (without lock) for performance
        if cls not in cls._instances:
            # Get or create lock for this specific class
            if cls not in cls._locks:
                with cls._meta_lock:
                    if cls not in cls._locks:
                        cls._locks[cls] = threading.Lock()

            # Acquire lock only for this specific class
            with cls._locks[cls]:
                # Second check (with lock) to prevent race condition
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance

        return cls._instances[cls]
