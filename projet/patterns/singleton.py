"""Simple Singleton metaclass and helper class.

This module provides a `Singleton` metaclass that can be applied to a
class to ensure only one instance exists. We also provide a convenience
`SingletonConfigurationManager` that wraps the existing
`ConfigurationManager` for users who prefer a singleton access pattern.
"""

from __future__ import annotations

from typing import Any

from projet.config import ConfigurationManager


class Singleton(type):
    """Metaclass implementing the Singleton pattern."""

    _instances: dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonConfigurationManager(ConfigurationManager, metaclass=Singleton):
    """Singleton wrapper around `ConfigurationManager`.

    Use this if you want a single shared configuration manager across
    the application:

        cfg = SingletonConfigurationManager()
        # subsequent calls return the same instance
    """

    pass
