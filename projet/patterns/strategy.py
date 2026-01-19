"""Strategy pattern example: different cleaning strategies for DataCleaner.

This module provides a small Strategy example: we define callable
cleaning strategies that can be passed to a processor to change behaviour
at runtime without changing the processor code.
"""

from __future__ import annotations

from typing import Callable
import pandas as pd


CleanStrategy = Callable[[pd.DataFrame], pd.DataFrame]


def remove_nulls(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna()


def fill_with_mean(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["number"]).columns:
        df[col] = df[col].fillna(df[col].mean())
    return df


class DataProcessor:
    def __init__(self, strategy: CleanStrategy) -> None:
        self.strategy = strategy

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.strategy(df)
