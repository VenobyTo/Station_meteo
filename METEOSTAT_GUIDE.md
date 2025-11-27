## API Data Retrieval - Meteostat Integration

This guide explains how to retrieve weather data from weather stations using the Meteostat API integration.

### Overview

The `MeteostatDataRetriever` class provides access to historical and current weather data from thousands of weather stations worldwide using the [Meteostat](https://meteostat.net) API.

### Installation

First, install the required dependencies:

```bash
pip install meteostat requests
```

Or use the provided requirements file:

```bash
pip install -r requirements.txt
```

### Features

- **Search stations**: Find weather stations by country code or name
- **Fetch by station ID**: Retrieve data for a specific station
- **Fetch by coordinates**: Automatically find and fetch data from the nearest station
- **Date range support**: Specify any historical date range
- **Automatic data cleaning**: Integrates with `DataCleaner` for normalized output

### Usage Examples

#### 1. Search for Weather Stations

```python
from projet import MeteostatDataRetriever

retriever = MeteostatDataRetriever()

# Search stations in France
stations = retriever.search_stations(country="FR")
print(stations.head())

# Search by name
paris_stations = retriever.search_stations(query="Orly", country="FR")
print(paris_stations)
```

#### 2. Fetch Data for a Specific Station

```python
from projet import MeteostatDataRetriever

retriever = MeteostatDataRetriever()

# Fetch data for Paris Orly airport (station ID: 10438)
df = retriever.fetch_by_station(
    station_id="10438",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

print(df.head())
print(df.describe())
```

#### 3. Fetch Data by Coordinates

```python
from projet import MeteostatDataRetriever

retriever = MeteostatDataRetriever()

# Fetch data for nearest station to Paris (48.8566°N, 2.3522°E)
df = retriever.fetch_by_coordinates(
    latitude=48.8566,
    longitude=2.3522,
    start_date="2023-01-01",
    end_date="2023-12-31",
    radius_km=25  # Search within 25km
)

print(df)
```

#### 4. Command Line Interface

##### Search stations
```bash
# Search all stations in France
python -m projet meteo search --country FR

# Search stations by name
python -m projet meteo search --query Orly --country FR
```

##### Fetch station data
```bash
# Get last year of data for Paris Orly
python -m projet meteo station 10438

# Specific date range
python -m projet meteo station 10438 --start 2024-01-01 --end 2024-01-31

# Show 10 rows instead of 5
python -m projet meteo station 10438 --sample 10
```

##### Fetch by coordinates
```bash
# Get data for nearest station to Paris
python -m projet meteo coords 48.8566 2.3522

# With date range and search radius
python -m projet meteo coords 48.8566 2.3522 --start 2024-01-01 --end 2024-01-31 --radius 50
```

### Available Data Columns

Meteostat provides the following weather parameters:

- **temp**: Temperature (°C)
- **dwpt**: Dew point (°C)
- **rhum**: Relative humidity (%)
- **prcp**: Precipitation (mm)
- **wdir**: Wind direction (°)
- **wspd**: Wind speed (km/h)
- **pres**: Pressure (hPa)

All data is automatically:
- Indexed by timezone-aware datetime (UTC)
- Converted to numeric types where appropriate
- Validated for correctness

### Common Station IDs

Some popular station IDs in France:

| Station | ID | Location | Notes |
|---------|-----|----------|-------|
| Paris Orly | 10438 | Paris | Major airport |
| Paris Le Bourget | 10383 | Paris | Alternative airport |
| Nice | 07690 | Nice | Mediterranean |
| Lyon Satolas | 07480 | Lyon | Major airport |
| Marseille | 07630 | Marseille | Major airport |
| Toulouse | 07620 | Toulouse | South-west France |

Find more IDs using the search functionality.

### Date Ranges

- **Default**: If no dates provided, retrieves last 365 days
- **String format**: "YYYY-MM-DD"
- **Python format**: `datetime` objects supported

```python
# These are equivalent
df1 = retriever.fetch_by_station("10438", "2024-01-01", "2024-12-31")
df2 = retriever.fetch_by_station("10438", datetime(2024, 1, 1), datetime(2024, 12, 31))
```

### Error Handling

```python
from projet import MeteostatDataRetriever

retriever = MeteostatDataRetriever()

try:
    df = retriever.fetch_by_station("invalid_id")
except ValueError as e:
    print(f"Error: {e}")
except ImportError as e:
    print(f"Meteostat not installed: {e}")
```

### Integration with Data Cleaning

The retrieved data is automatically cleaned:

```python
from projet import MeteostatDataRetriever, DataCleaner

# Custom cleaner with specific timezone
cleaner = DataCleaner(tz="Europe/Paris")
retriever = MeteostatDataRetriever(cleaner)

df = retriever.fetch_by_station("10438", "2024-01-01")
# Data is automatically:
# - Indexed by Europe/Paris timezone
# - Column names normalized
# - Numeric types coerced
```

### Performance Considerations

- **API calls**: Meteostat has rate limits (typically 2 requests/sec)
- **Caching**: Consider caching results locally to reduce API calls
- **Date ranges**: Smaller date ranges = faster retrieval
- **Coordinate searches**: Nearby() calls fetch all stations, can be slow on first use

### Testing

Run the test suite:

```bash
python -m pytest tests/test_meteostat.py -v

# With coverage
python -m pytest tests/ --cov=projet
```

### Examples

See `examples.py` for complete working examples:

```bash
python examples.py
```

### Troubleshooting

**Issue**: ImportError: meteostat library is required

**Solution**: Install meteostat: `pip install meteostat`

---

**Issue**: ValueError: Station {id} not found

**Solution**: Use the search command to find valid station IDs

---

**Issue**: No data found for date range

**Solution**: Check that:
1. Station ID is valid
2. Date range is within available data (use `search` to see available periods)
3. Station had observations for that period

### References

- [Meteostat Documentation](https://dev.meteostat.net)
- [Available Stations](https://meteostat.net/en/station)
- [Data Documentation](https://dev.meteostat.net/docs)
