"""Patterns package.

Exports the pattern modules for convenient imports, e.g.:

    from projet.patterns import factory, singleton, observer, strategy

"""

from . import factory  # noqa: F401
from . import singleton  # noqa: F401
from . import observer  # noqa: F401
from . import strategy  # noqa: F401

__all__ = ["factory", "singleton", "observer", "strategy"]
