# Station Méteo

A clean Python package for weather data retrieval, cleaning, and analysis.

## Features

- **CSV Data Retrieval**: Load and validate weather data from CSV files
- **Data Cleaning**: Automatic column normalization, timestamp parsing, and type coercion
- **Timezone Support**: Parse and convert timestamps to any timezone (UTC by default)
- **Clean Architecture**: Organized into focused modules with clear separation of concerns

## Project Structure

```
projet/
├── __init__.py       # Package exports
├── __main__.py       # Entry point for python -m projet
├── cleaner.py        # DataCleaner class for data normalization
├── retriever.py      # DataRetriever abstract class and CSVDataRetriever
└── cli.py            # WeatherApp CLI orchestration

tests/
├── __init__.py
├── conftest.py       # pytest configuration
└── test_csv_retriever.py  # Unit tests
```

## Installation

Install in development mode:

```bash
pip install -e .
```

Or with dev dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

### As a module

```python
from projet.retriever import CSVDataRetriever
from projet.cleaner import DataCleaner

cleaner = DataCleaner(tz="Europe/Paris")
retriever = CSVDataRetriever(cleaner)
df = retriever.fetch("data.csv")
print(df)
```

### From command line

```bash
# Using python -m
python -m projet path/to/file.csv --tz "Europe/Paris" --sample 10

# Or directly
station-meteo path/to/file.csv
```

## Running Tests

```bash
pytest tests/
pytest tests/ -v  # verbose
pytest tests/ --cov=projet  # with coverage
```

## Clean Code Principles Applied

- ✅ Small, single-responsibility classes
- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Separation of concerns (retrieval, cleaning, CLI)
- ✅ Dependency injection
- ✅ No module-level side effects
- ✅ Testable design

## Requirements

- Python >= 3.10
- pandas >= 1.3
- pyarrow >= 6.0.0
