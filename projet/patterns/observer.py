"""Observer / Subject utilities.

This module implements a minimal Observer pattern: a `Subject` can have
callable subscribers which are notified with `(event_name, payload)` when
`notify` is called. We also provide `ObservableRetriever` which wraps any
retriever and emits `fetched` events when data is fetched.
"""

from __future__ import annotations

from typing import Callable, Any

from projet.retriever import DataRetriever
import pandas as pd


Subscriber = Callable[[str, Any], None]


class Subject:
    """A simple subject that holds subscribers and notifies them."""

    def __init__(self) -> None:
        self._subs: list[Subscriber] = []

    def subscribe(self, fn: Subscriber) -> None:
        """Add a subscriber callable(fn(event_name, payload))."""
        if fn not in self._subs:
            self._subs.append(fn)

    def unsubscribe(self, fn: Subscriber) -> None:
        if fn in self._subs:
            self._subs.remove(fn)

    def notify(self, event: str, payload: Any = None) -> None:
        for fn in list(self._subs):
            try:
                fn(event, payload)
            except Exception:
                # subscriber exceptions shouldn't break the subject
                pass


class ObservableRetriever:
    """Wrap a DataRetriever and emit events on fetch operations.

    Emits events:
      - 'fetch:start' with payload {'args':..., 'kwargs':...}
      - 'fetch:done' with payload DataFrame
      - 'fetch:error' with payload Exception
    """

    def __init__(self, retriever: DataRetriever) -> None:
        self.retriever = retriever
        self.events = Subject()

    def fetch(self, *args, **kwargs) -> pd.DataFrame:
        self.events.notify("fetch:start", {"args": args, "kwargs": kwargs})
        try:
            df = self.retriever.fetch(*args, **kwargs)
            self.events.notify("fetch:done", df)
            return df
        except Exception as exc:  # pragma: no cover - surface errors
            self.events.notify("fetch:error", exc)
            raise
