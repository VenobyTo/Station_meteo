"""Data cleaning and normalization utilities."""

from __future__ import annotations

import logging
from typing import Iterable, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DataCleaner:
    """Encapsulates cleaning operations for weather dataframes.

    Provides methods for normalization, timestamp parsing, and type coercion.
    Use clean() to run the full pipeline.

    Attributes:
        timestamp_candidates: Column names to search for timestamps.
        parse_dates: Whether to parse string timestamps.
        tz: Target timezone (default: UTC).
    """

    DEFAULT_TIMESTAMP_CANDIDATES = ["timestamp", "date", "datetime", "time"]

    def __init__(
        self,
        timestamp_candidates: Iterable[str] | None = None,
        parse_dates: bool = True,
        tz: str = "UTC",
    ) -> None:
        if timestamp_candidates is None:
            timestamp_candidates = self.DEFAULT_TIMESTAMP_CANDIDATES
        self.timestamp_candidates = list(timestamp_candidates)
        self.parse_dates = parse_dates
        self.tz = tz

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names: strip whitespace and convert to lowercase.

        Args:
            df: Input DataFrame.

        Returns:
            DataFrame with normalized column names.
        """
        mapping = {c: str(c).strip().lower() for c in df.columns}
        return df.rename(columns=mapping)

    def find_timestamp_column(self, columns: Iterable[str]) -> Optional[str]:
        """Find the timestamp column by name or heuristic.

        Args:
            columns: Column names to search.

        Returns:
            Column name if found; None otherwise.
        """
        cols = list(columns)

        # first pass: exact match from candidates
        for cand in self.timestamp_candidates:
            if cand in cols:
                return cand

        # fallback: heuristic match on "date" or "time"
        for c in cols:
            if "date" in c or "time" in c:
                return c

        return None

    def parse_and_set_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse timestamp column and set timezone-aware DatetimeIndex.

        Args:
            df: Input DataFrame.

        Returns:
            DataFrame with datetime index.

        Raises:
            ValueError: If no timestamp column is found.
        """
        ts_col = self.find_timestamp_column(df.columns)
        if ts_col is None:
            raise ValueError(
                f"No timestamp column found. Searched: {self.timestamp_candidates}"
            )

        if self.parse_dates:
            df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")

        # drop rows with invalid timestamps
        before = len(df)
        df = df[~df[ts_col].isna()].copy()
        dropped = before - len(df)
        if dropped:
            logger.warning("Dropped %d rows with invalid timestamps", dropped)

        # ensure timezone-aware index
        if df[ts_col].dt.tz is None:
            try:
                df[ts_col] = df[ts_col].dt.tz_localize(
                    self.tz, ambiguous="infer", nonexistent="shift_forward"
                )
            except Exception:
                logger.debug(
                    "Could not localize timestamps to %s; leaving naive datetimes",
                    self.tz,
                )
        else:
            try:
                df[ts_col] = df[ts_col].dt.tz_convert(self.tz)
            except Exception:
                logger.debug("Could not convert timezone to %s", self.tz)

        df = df.set_index(ts_col)
        df.index.name = "timestamp"
        return df

    def coerce_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert object columns to numeric where appropriate.

        Args:
            df: Input DataFrame.

        Returns:
            DataFrame with numeric columns coerced.
        """
        for col in df.columns:
            if df[col].dtype == object:
                coerced = pd.to_numeric(df[col], errors="ignore")
                if coerced.dtype != object:
                    df[col] = coerced
        return df

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run full cleaning pipeline: normalize, parse index, coerce types.

        Args:
            df: Raw input DataFrame.

        Returns:
            Cleaned DataFrame.
        """
        df = self.normalize_columns(df)
        df = self.parse_and_set_index(df)
        df = self.coerce_numeric_columns(df)
        return df
