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
└── test_*.py         # Unit tests
```

## Installation

Install in development mode:

```powershell
pip install -e .
```

Or with dev dependencies:

```powershell
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
print(df.head())
```

### From command line

```powershell
# Using python -m
python -m projet csv path/to/file.csv --tz "Europe/Paris" --sample 10

# Example: list stations using bundled filename
python -m projet stations --source toulouse --limit 10
```

## Design Patterns Used

- **Manager pattern**: `ConfigurationManager` in `projet/config.py` centralizes config lifecycle.
- **Factory/Provider pattern**: Retriever classes in `projet/retriever.py` provide data from different sources.
- **Strategy / Dependency Injection**: `DataCleaner` injected into `CSVDataRetriever` to allow different cleaning strategies.

## Requirements

- Python >= 3.10
- pandas >= 1.3
- pyarrow >= 6.0.0

## Next steps / Optional checks

- Run `pylint` or `ruff` for linting and style enforcement (not required here but recommended).
- Add CI workflow to run tests and linters automatically on push.
