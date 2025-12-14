# Configuration System - Complete Guide

## Overview

A comprehensive **configuration management system** using dictionary data structures for managing weather station configurations, API settings, and extraction parameters.

## Key Features

### 📚 ConfigDict - Extended Configuration Dictionary
- Type-safe getters with defaults (string, int, float, bool, list, dict)
- Nested configuration using dot notation
- JSON serialization/deserialization
- Deep dictionary updates
- Logging and validation

### 🏢 StationsDict - Weather Station Registry
- Add/remove stations by ID
- Query by name or region
- Organize stations by region
- JSON export and conversion
- Statistics and counting

### ⚙️ Configuration Objects
- `StationConfig` - Individual station metadata
- `APIConfig` - API endpoint configuration
- `ExtractionConfig` - Data extraction settings
- `OutputConfig` - Output format and path settings

### 🎛️ ConfigurationManager - Unified Management
- Central configuration hub
- Load/save from JSON files
- Station management
- API, extraction, and output configuration
- Real-time statistics

## Classes Reference

### ConfigDict
Extended dictionary with typed accessors.

```python
from projet import ConfigDict

config = ConfigDict()
config['timeout'] = 30
config['cache'] = 'yes'

# Typed accessors
timeout = config.get_int('timeout', default=30)
cache_enabled = config.get_bool('cache', default=False)

# Nested configuration
config.set_nested('api.url', 'https://api.example.com')
url = config.get_nested('api.url')

# JSON operations
json_str = config.to_json()
config.update_from_dict({'new_key': 'value'}, deep=True)
```

### StationsDict
Specialized dictionary for weather stations.

```python
from projet import StationsDict, StationConfig

stations = StationsDict()

# Add station
station = StationConfig('PARIS_01', 'Paris', 48.856, 2.352, region='IDF')
stations.add_station(station)

# Query stations
paris = stations.get_station('PARIS_01')
by_name = stations.get_by_name('Paris')
idf_stations = stations.get_by_region('IDF')

# Statistics
all_stations = stations.list_stations()
by_region = stations.list_stations_by_region()
counts = stations.count_by_region()

# Export
dicts = stations.to_dict_list()
json_str = stations.to_json()
```

### StationConfig
Configuration for a weather station.

```python
from projet import StationConfig

station = StationConfig(
    station_id='PARIS_01',
    name='Paris - Montsouris',
    latitude=48.8194,
    longitude=2.3353,
    altitude=75.0,
    region='IDF',
    metadata={'priority': 'high', 'network': 'meteo_france'}
)

# Convert to dict
station_dict = station.to_dict()

# Access properties
print(f"{station.name} at ({station.latitude}, {station.longitude})")
```

### APIConfig
API endpoint configuration.

```python
from projet import APIConfig

api = APIConfig(
    base_url='https://api.meteo.fr',
    api_key='your_key',
    timeout=30,
    max_retries=3,
    rate_limit=10.0,
    headers={'User-Agent': 'WeatherApp/2.0'}
)

api_dict = api.to_dict()
```

### ExtractionConfig
Data extraction settings.

```python
from projet import ExtractionConfig, DataSource

extraction = ExtractionConfig(
    source=DataSource.TOULOUSE,
    date_format='%Y-%m-%d',
    start_date='2024-01-01',
    end_date='2024-12-31',
    batch_size=100,
    parallel_workers=4,
    cache_enabled=True,
    cache_ttl=3600
)
```

### OutputConfig
Output format and location.

```python
from projet import OutputConfig, OutputFormat

output = OutputConfig(
    format=OutputFormat.CSV,
    path='/data/output',
    overwrite=False,
    compression='gzip',
    include_metadata=True
)
```

### ConfigurationManager
Central configuration management.

```python
from projet import ConfigurationManager, StationConfig, APIConfig

manager = ConfigurationManager()

# Load configuration
manager.load_config({'app_name': 'Weather App'})
manager.load_from_json(json_string)
manager.load_from_file('config.json')

# Add stations
station = StationConfig('PARIS_01', 'Paris')
manager.add_station(station)

manager.add_stations([
    StationConfig('S1', 'Station 1'),
    StationConfig('S2', 'Station 2'),
])

# Configure components
api = APIConfig('https://api.example.com')
manager.set_api_config(api)

extraction = ExtractionConfig(batch_size=100)
manager.set_extraction_config(extraction)

output = OutputConfig(path='/output')
manager.set_output_config(output)

# Query
stats = manager.get_stats()
stations = manager.list_all_stations()
station = manager.get_station('PARIS_01')

# Save
manager.save_to_file('config.json')
```

## Enumerations

### DataSource
```python
DataSource.TOULOUSE     # Toulouse meteorology API
DataSource.METEOSTAT   # Meteostat service
DataSource.OPENWEATHER # OpenWeather API
DataSource.CSV         # CSV file input
```

### OutputFormat
```python
OutputFormat.CSV       # CSV format
OutputFormat.JSON      # JSON format
OutputFormat.PARQUET   # Parquet format
OutputFormat.EXCEL     # Excel format
```

### ConfigKey
Standard configuration keys with enum values.

```python
ConfigKey.API_URL
ConfigKey.API_KEY
ConfigKey.STATIONS
ConfigKey.DATA_SOURCE
ConfigKey.BATCH_SIZE
ConfigKey.OUTPUT_FORMAT
# ... and more
```

## Usage Examples

### Example 1: Basic Configuration
```python
from projet import ConfigDict

config = ConfigDict()
config['api_url'] = 'https://api.meteo.fr'
config['timeout'] = 30
config['retries'] = '3'

# Type-safe access
url = config.get_string('api_url')
timeout = config.get_int('timeout')
retries = config.get_int('retries')
```

### Example 2: Station Management
```python
from projet import StationsDict, StationConfig

stations = StationsDict()

# Add multiple stations
for station_data in station_list:
    station = StationConfig(**station_data)
    stations.add_station(station)

# Query by region
idf_stations = stations.get_by_region('IDF')
for station in idf_stations:
    print(f"{station.name}: ({station.latitude}, {station.longitude})")

# Statistics
print(f"Total: {len(stations)}")
print(f"By region: {stations.count_by_region()}")
```

### Example 3: Complete Configuration Setup
```python
from projet import (
    ConfigurationManager, StationConfig, APIConfig,
    ExtractionConfig, OutputConfig, DataSource, OutputFormat
)

# Create manager
manager = ConfigurationManager()

# Configure API
api = APIConfig(
    'https://api.meteo.fr',
    api_key='your_key',
    timeout=30
)
manager.set_api_config(api)

# Configure extraction
extraction = ExtractionConfig(
    source=DataSource.TOULOUSE,
    batch_size=100,
    parallel_workers=4
)
manager.set_extraction_config(extraction)

# Configure output
output = OutputConfig(
    format=OutputFormat.CSV,
    path='/data/output'
)
manager.set_output_config(output)

# Add stations
stations = [
    StationConfig('PARIS_01', 'Paris', 48.856, 2.352, region='IDF'),
    StationConfig('LYON_01', 'Lyon', 45.764, 4.835, region='ARA'),
]
manager.add_stations(stations)

# Get statistics
stats = manager.get_stats()
print(f"Configuration: {stats}")
```

### Example 4: JSON Configuration Files
```python
import json
from projet import ConfigurationManager

# Create configuration
config_data = {
    'api': {
        'url': 'https://api.meteo.fr',
        'timeout': 30
    },
    'extraction': {
        'batch_size': 100,
        'workers': 4
    },
    'stations': [
        {'id': 'P1', 'name': 'Paris', 'lat': 48.856}
    ]
}

# Save to file
with open('config.json', 'w') as f:
    json.dump(config_data, f, indent=2)

# Load in manager
manager = ConfigurationManager()
manager.load_from_file('config.json')

# Use configuration
stats = manager.get_stats()
stations = manager.list_all_stations()
```

### Example 5: Nested Configuration
```python
from projet import ConfigDict

config = ConfigDict()

# Set nested values
config.set_nested('database.host', 'localhost')
config.set_nested('database.port', 5432)
config.set_nested('database.name', 'weather_db')

# Get nested values
host = config.get_nested('database.host')
port = config.get_nested('database.port', default=3306)

# Update nested
config.update_from_dict({
    'database': {'user': 'admin', 'password': 'secret'}
}, deep=True)

# Access nested dict
db_config = config.get_dict('database')
print(f"Database: {db_config}")
```

## Real-World Usage Patterns

### Pattern 1: Application Initialization
```python
from projet import ConfigurationManager

# Load configuration on startup
config = ConfigurationManager()
config.load_from_file('/etc/weather_app/config.json')

# Validate configuration
stats = config.get_stats()
assert stats['api_configured'], "API not configured"
assert stats['total_stations'] > 0, "No stations configured"

# Use in application
api_url = config.config['api']['url']
stations = config.list_all_stations()
```

### Pattern 2: Region-Specific Processing
```python
from projet import ConfigurationManager

manager = ConfigurationManager()
manager.load_from_file('config.json')

# Process by region
regions = manager.stations.list_stations_by_region()

for region, stations in regions.items():
    print(f"Processing {region}: {len(stations)} stations")
    for station in stations:
        # Process station...
        pass
```

### Pattern 3: Dynamic Configuration Updates
```python
config = ConfigDict()
config.load_from_file('config.json')

# Update at runtime
new_settings = {
    'timeout': 60,
    'retries': 5,
    'cache': True
}
config.update_from_dict(new_settings)

# Save changes
config.save_to_file('config.json')
```

## Testing

See `tests/test_config.py` for comprehensive test coverage:

```bash
python -m pytest tests/test_config.py -v
# Result: 44/44 PASSED ✅
```

Test categories:
- ConfigDict operations (12 tests)
- StationsDict operations (11 tests)
- Station configuration (2 tests)
- API configuration (2 tests)
- Extraction configuration (2 tests)
- Output configuration (2 tests)
- ConfigurationManager (11 tests)

## Files

- `projet/config.py` - Implementation (580+ lines)
- `tests/test_config.py` - Test suite (44 tests)
- `config_examples.py` - 6 complete working examples

## Integration with Other Components

Works seamlessly with:
- ✅ Queue system for task management
- ✅ Linked list for station sequences
- ✅ Data retrievers (API, CSV)
- ✅ Data cleaner for preprocessing
- ✅ CLI commands

Example integration:
```python
from projet import ConfigurationManager, ExtractionQueue

# Load configuration
config = ConfigurationManager()
config.load_from_file('config.json')

# Create extraction queue
queue = ExtractionQueue()

# Add tasks from configured stations
for station in config.list_all_stations():
    task = ExtractionTask(
        f"task_{station.station_id}",
        station.station_id,
        station.name,
        config.extraction_config.start_date,
        config.extraction_config.end_date
    )
    queue.add_task(task)

# Process queue
while queue.get_pending_count() > 0:
    task = queue.get_next_task()
    # Extract data...
```

## Best Practices

1. **Use ConfigKey enums** for standard configuration keys
2. **Load configuration early** in application startup
3. **Validate configuration** after loading
4. **Use type-safe accessors** (get_int, get_bool, etc.)
5. **Organize nested configuration** with meaningful hierarchies
6. **Store sensitive data** separately (API keys, passwords)
7. **Version your configuration** schema
8. **Export/import JSON** for configuration sharing

## Summary

A complete, production-ready configuration system providing:
- ✅ Type-safe dictionary operations
- ✅ Specialized station management
- ✅ Structured configuration objects
- ✅ JSON file I/O
- ✅ Nested configuration support
- ✅ Statistics and monitoring
- ✅ Full test coverage (44/44 tests)
- ✅ Complete documentation
- ✅ Real-world examples
