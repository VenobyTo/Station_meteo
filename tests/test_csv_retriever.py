"""Unit tests for CSV data retriever."""

import pandas as pd
import pytest

from projet.cleaner import DataCleaner
from projet.retriever import CSVDataRetriever


SAMPLE_CSV = """date,temperature,wind
2020-01-01 00:00,10.0,3.2
2020-01-01 01:00,9.5,2.8
2020-01-01 02:00,,2.6
"""


def test_csv_retriever_load(tmp_path):
    """Test that CSVDataRetriever loads and cleans a CSV file."""
    p = tmp_path / "sample.csv"
    p.write_text(SAMPLE_CSV)

    retriever = CSVDataRetriever(DataCleaner())
    df = retriever.fetch(str(p))

    assert "temperature" in df.columns
    assert df.index.name == "timestamp"
    assert len(df) == 3


def test_csv_retriever_file_not_found():
    """Test that FileNotFoundError is raised for missing files."""
    retriever = CSVDataRetriever()
    with pytest.raises(FileNotFoundError):
        retriever.fetch("/nonexistent/path.csv")


def test_data_cleaner_numeric_coercion(tmp_path):
    """Test that numeric columns are coerced correctly."""
    csv = "date,val\n2020-01-01 00:00,1\n2020-01-01 01:00,2\n"
    p = tmp_path / "num.csv"
    p.write_text(csv)

    retriever = CSVDataRetriever(DataCleaner())
    df = retriever.fetch(str(p))

    assert df["val"].dtype.kind in "iuf"  # int/unsigned/float


def test_data_cleaner_normalize_columns():
    """Test that columns are normalized to lowercase."""
    cleaner = DataCleaner()
    df = pd.DataFrame({"  DATE  ": [1, 2], "Temperature": [20, 21]})
    df_norm = cleaner.normalize_columns(df)

    assert "  date  ".lower() in df_norm.columns or "date" in df_norm.columns
