"""Factory for creating DataRetriever instances based on a source key.

This module implements a simple Factory pattern to centralize the
creation of retriever objects (CSV, Toulouse API, Meteostat). It keeps
construction logic in one place and makes client code simpler.
"""

from __future__ import annotations

from typing import Optional

from projet.cleaner import DataCleaner
from projet.retriever import DataRetriever, CSVDataRetriever
from projet.api import ToulouseMeteoAPIRetriever, MeteostatDataRetriever


def get_retriever(source: str, cleaner: Optional[DataCleaner] = None) -> DataRetriever:
    """Return a DataRetriever instance for the given source key.

    Args:
        source: One of 'csv', 'toulouse', 'meteostat' (case-insensitive).
        cleaner: Optional `DataCleaner` instance to inject.

    Returns:
        An instance of a subclass of `DataRetriever`.

    Raises:
        ValueError: if the source key is unknown.
    """
    key = (source or "").strip().lower()
    cleaner = cleaner or DataCleaner()

    if key in ("csv", "file"):
        return CSVDataRetriever(cleaner)
    if key == "toulouse":
        return ToulouseMeteoAPIRetriever(cleaner)
    if key == "meteostat":
        return MeteostatDataRetriever(cleaner)

    raise ValueError(f"Unknown retriever source: {source}")
