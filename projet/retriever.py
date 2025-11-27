"""Data retrieval abstractions and implementations."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from projet.cleaner import DataCleaner

logger = logging.getLogger(__name__)


class DataRetriever(ABC):
    """Abstract interface for data retrieval implementations.

    All retrievers must return a DataFrame indexed by a timezone-aware
    DatetimeIndex (UTC by default) or raise an exception.
    """

    @abstractmethod
    def fetch(self, *args, **kwargs) -> pd.DataFrame:
        """Fetch and return a cleaned pandas.DataFrame."""
        raise NotImplementedError


class CSVDataRetriever(DataRetriever):
    """CSV data retriever with light cleaning and validation.

    Usage:
        cleaner = DataCleaner()
        retriever = CSVDataRetriever(cleaner)
        df = retriever.fetch("path/to/file.csv")
    """

    def __init__(self, cleaner: DataCleaner | None = None) -> None:
        self.cleaner = cleaner or DataCleaner()

    def fetch(
        self, filepath: str | Path, usecols: Optional[Iterable[str]] = None
    ) -> pd.DataFrame:
        """Load CSV and apply cleaning.

        Args:
            filepath: Path to the CSV file.
            usecols: Optional subset of columns to read.

        Returns:
            Cleaned DataFrame indexed by timezone-aware datetime.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If no timestamp column is found.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        df = pd.read_csv(
            path, usecols=list(usecols) if usecols is not None else None
        )
        df = self.cleaner.clean(df)

        logger.info(
            "Loaded %d rows and %d columns from %s",
            len(df),
            len(df.columns),
            path.name,
        )
        return df
