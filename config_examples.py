"""Examples of configuration system usage."""

import json
from projet.config import (
    ConfigDict, StationsDict, ConfigurationManager,
    StationConfig, APIConfig, ExtractionConfig, OutputConfig,
    DataSource, OutputFormat
)


def example1_basic_config_dict():
    """Example 1: Basic ConfigDict operations."""
    print("\n" + "="*70)
    print("Example 1: Basic ConfigDict Operations")
    print("="*70)
    
    # Create config dictionary
    config = ConfigDict()
    
    # Add configuration values
    config['api_url'] = 'https://api.meteo.fr'
    config['timeout'] = 30
    config['retries'] = '3'
    config['cache_enabled'] = 'yes'
    
    print(f"\nConfiguration created: {config}")
    print(f"URL: {config.get_string('api_url')}")
    print(f"Timeout: {config.get_int('timeout')} seconds")
    print(f"Retries: {config.get_int('retries')}")
    print(f"Cache: {config.get_bool('cache_enabled')}")
    
    # Nested configuration
    config.set_nested('api.timeout', 60)
    config.set_nested('api.key', 'secret_key')
    
    print(f"\nNested configuration:")
    print(f"API Timeout: {config.get_nested('api.timeout')}")
    print(f"API Key: {config.get_nested('api.key')}")


def example2_stations_dict():
    """Example 2: StationsDict for managing weather stations."""
    print("\n" + "="*70)
    print("Example 2: StationsDict - Station Management")
    print("="*70)
    
    # Create stations dictionary
    stations = StationsDict()
    
    # Add stations
    print("\nAdding stations...")
    stations_data = [
        StationConfig('PARIS_01', 'Paris - Montsouris', 48.8194, 2.3353, region='IDF'),
        StationConfig('PARIS_02', 'Paris - Le Bourget', 48.9695, 2.4392, region='IDF'),
        StationConfig('LYON_01', 'Lyon - Brotteaux', 45.7640, 4.8357, region='ARA'),
        StationConfig('MARSEILLE_01', 'Marseille - Marignane', 43.4426, 5.2184, region='PACA'),
    ]
    
    for station in stations_data:
        stations.add_station(station)
        print(f"  ✓ {station}")
    
    # Query stations
    print(f"\nTotal stations: {len(stations)}")
    print(f"Paris stations: {len(stations.get_by_region('IDF'))}")
    print(f"Lyon stations: {len(stations.get_by_region('ARA'))}")
    
    # Get station by name
    paris = stations.get_by_name('Paris - Montsouris')
    print(f"\nFound station: {paris}")
    print(f"  Location: ({paris.latitude}, {paris.longitude})")
    
    # Statistics
    print(f"\nStations by region:")
    for region, count in stations.count_by_region().items():
        print(f"  {region}: {count} stations")


def example3_configuration_manager():
    """Example 3: ConfigurationManager - Complete configuration system."""
    print("\n" + "="*70)
    print("Example 3: ConfigurationManager - Full Configuration")
    print("="*70)
    
    # Create manager
    manager = ConfigurationManager()
    print(f"\nConfigurationManager created: {manager}")
    
    # Load base configuration
    base_config = {
        'app_name': 'Weather Station Extractor',
        'version': '2.0',
        'debug': False,
        'log_level': 'INFO'
    }
    manager.load_config(base_config)
    print(f"✓ Base configuration loaded")
    
    # Configure API
    api = APIConfig(
        'https://api.meteo.fr',
        api_key='your_api_key',
        timeout=30,
        max_retries=3
    )
    manager.set_api_config(api)
    print(f"✓ API configuration set")
    
    # Configure extraction
    extraction = ExtractionConfig(
        source=DataSource.TOULOUSE,
        batch_size=100,
        parallel_workers=4,
        cache_enabled=True
    )
    manager.set_extraction_config(extraction)
    print(f"✓ Extraction configuration set")
    
    # Configure output
    output = OutputConfig(
        format=OutputFormat.CSV,
        path='/data/output',
        overwrite=False
    )
    manager.set_output_config(output)
    print(f"✓ Output configuration set")
    
    # Add stations
    print(f"\nAdding stations to manager...")
    stations = [
        StationConfig('PARIS_01', 'Paris', 48.856, 2.352, region='IDF'),
        StationConfig('LYON_01', 'Lyon', 45.764, 4.835, region='ARA'),
    ]
    manager.add_stations(stations)
    print(f"✓ {manager.get_station_count()} stations configured")
    
    # Display statistics
    print(f"\nConfiguration Statistics:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def example4_json_configuration():
    """Example 4: Loading and saving JSON configuration."""
    print("\n" + "="*70)
    print("Example 4: JSON Configuration Management")
    print("="*70)
    
    # Create configuration as JSON
    config_json = {
        'application': {
            'name': 'Weather Station System',
            'version': '2.0'
        },
        'api': {
            'url': 'https://api.meteo.fr',
            'timeout': 30,
            'retries': 3
        },
        'extraction': {
            'source': 'toulouse',
            'batch_size': 100
        },
        'stations': [
            {'id': 'P1', 'name': 'Paris', 'lat': 48.856, 'lon': 2.352},
            {'id': 'L1', 'name': 'Lyon', 'lat': 45.764, 'lon': 4.835}
        ]
    }
    
    # Convert to JSON string
    json_str = json.dumps(config_json, indent=2)
    print(f"\nConfiguration JSON:")
    print(json_str[:200] + "...")
    
    # Load into manager
    manager = ConfigurationManager()
    manager.load_from_json(json_str)
    
    print(f"\n✓ Configuration loaded from JSON")
    print(f"  App: {manager.get_config('application')}")
    print(f"  API URL: {manager.config.get_nested('api.url')}")
    print(f"  Batch Size: {manager.config.get_nested('extraction.batch_size')}")


def example5_advanced_config_operations():
    """Example 5: Advanced configuration operations."""
    print("\n" + "="*70)
    print("Example 5: Advanced Configuration Operations")
    print("="*70)
    
    config = ConfigDict({
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'weather_db'
        },
        'cache': {
            'enabled': True,
            'ttl': 3600
        }
    })
    
    print(f"\nInitial configuration:")
    print(f"  Database: {config.get_dict('database')}")
    print(f"  Cache: {config.get_dict('cache')}")
    
    # Update configuration
    updates = {
        'database': {
            'user': 'admin'
        },
        'logging': {
            'level': 'DEBUG'
        }
    }
    
    config.update_from_dict(updates, deep=True)
    
    print(f"\nAfter update:")
    print(f"  Database: {config.get_dict('database')}")
    print(f"  Has user: {'user' in config.get_dict('database')}")
    print(f"  Logging: {config.get_dict('logging')}")
    
    # Export to JSON
    json_output = config.to_json()
    print(f"\nJSON export (first 100 chars):")
    print(f"  {json_output[:100]}...")


def example6_multi_region_configuration():
    """Example 6: Multi-region station configuration."""
    print("\n" + "="*70)
    print("Example 6: Multi-Region Station Configuration")
    print("="*70)
    
    manager = ConfigurationManager()
    
    # Create stations for multiple regions
    stations_config = [
        # Île-de-France
        ('PARIS_01', 'Paris - Montsouris', 48.8194, 2.3353, 'IDF'),
        ('VERSAILLES_01', 'Versailles', 48.8044, 2.1299, 'IDF'),
        # Auvergne-Rhône-Alpes
        ('LYON_01', 'Lyon - Brotteaux', 45.7640, 4.8357, 'ARA'),
        ('SAINT_ETIENNE_01', 'Saint-Étienne', 45.4398, 4.3882, 'ARA'),
        # PACA
        ('MARSEILLE_01', 'Marseille', 43.4426, 5.2184, 'PACA'),
        ('NICE_01', 'Nice', 43.7102, 7.2026, 'PACA'),
    ]
    
    print(f"\nAdding {len(stations_config)} stations across regions...")
    for station_id, name, lat, lon, region in stations_config:
        station = StationConfig(station_id, name, lat, lon, region=region)
        manager.add_station(station)
    
    print(f"✓ {manager.get_station_count()} stations added")
    
    # Analyze by region
    print(f"\nStations by region:")
    regions_dict = manager.stations.list_stations_by_region()
    for region, stations_list in sorted(regions_dict.items()):
        print(f"\n  {region}:")
        for station in stations_list:
            print(f"    • {station.name} ({station.station_id})")
    
    # Get statistics
    region_counts = manager.stations.count_by_region()
    print(f"\nRegion statistics:")
    for region, count in sorted(region_counts.items()):
        print(f"  {region}: {count} stations")


if __name__ == "__main__":
    print("\n" + "█"*70)
    print("█  Configuration Examples - Weather Station System")
    print("█"*70)
    
    example1_basic_config_dict()
    example2_stations_dict()
    example3_configuration_manager()
    example4_json_configuration()
    example5_advanced_config_operations()
    example6_multi_region_configuration()
    
    print("\n" + "█"*70)
    print("█  All examples completed successfully!")
    print("█"*70 + "\n")
