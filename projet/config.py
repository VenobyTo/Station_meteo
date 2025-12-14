"""Configuration management system using dictionary data structures.

This module provides comprehensive configuration handling for weather data
retrieval, including API endpoints, station definitions, and extraction settings.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, Dict, List, Iterator, Union
import json

logger = logging.getLogger(__name__)


class ConfigKey(Enum):
    """Standard configuration keys."""
    
    # API Configuration
    API_URL = "api_url"
    API_KEY = "api_key"
    API_TIMEOUT = "api_timeout"
    API_RETRIES = "api_retries"
    
    # Station Configuration
    STATIONS = "stations"
    STATION_ID = "station_id"
    STATION_NAME = "station_name"
    STATION_LAT = "latitude"
    STATION_LON = "longitude"
    
    # Data Configuration
    DATA_SOURCE = "data_source"
    DATE_FORMAT = "date_format"
    START_DATE = "start_date"
    END_DATE = "end_date"
    
    # Processing Configuration
    BATCH_SIZE = "batch_size"
    PARALLEL_WORKERS = "parallel_workers"
    CACHE_ENABLED = "cache_enabled"
    CACHE_TTL = "cache_ttl"
    
    # Output Configuration
    OUTPUT_FORMAT = "output_format"
    OUTPUT_PATH = "output_path"
    LOG_LEVEL = "log_level"


class DataSource(Enum):
    """Supported data sources."""
    TOULOUSE = "toulouse"
    METEOSTAT = "meteostat"
    OPENWEATHER = "openweather"
    CSV = "csv"


class OutputFormat(Enum):
    """Supported output formats."""
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    EXCEL = "excel"


@dataclass
class StationConfig:
    """Configuration for a single weather station.
    
    Attributes:
        station_id: Unique station identifier
        name: Human-readable station name
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        altitude: Altitude in meters
        region: Geographic region/department
        metadata: Additional metadata
    """
    
    station_id: str
    name: str
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0
    region: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.name} ({self.station_id}) - {self.region}"
    
    def __repr__(self) -> str:
        """String representation."""
        return f"StationConfig(id={self.station_id}, name={self.name})"


@dataclass
class APIConfig:
    """API configuration settings.
    
    Attributes:
        base_url: Base URL for API endpoints
        api_key: API authentication key
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        rate_limit: Requests per second limit
        headers: Custom HTTP headers
    """
    
    base_url: str
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    rate_limit: float = 10.0
    headers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"APIConfig(url={self.base_url}, timeout={self.timeout}s)"


@dataclass
class ExtractionConfig:
    """Data extraction configuration.
    
    Attributes:
        source: Data source type
        date_format: Date format string
        start_date: Default start date
        end_date: Default end date
        batch_size: Batch processing size
        parallel_workers: Number of parallel workers
        cache_enabled: Enable caching
        cache_ttl: Cache time-to-live in seconds
    """
    
    source: DataSource = DataSource.TOULOUSE
    date_format: str = "%Y-%m-%d"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    batch_size: int = 100
    parallel_workers: int = 4
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        config_dict = asdict(self)
        config_dict['source'] = self.source.value
        return config_dict
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return (
            f"ExtractionConfig(source={self.source.value}, "
            f"batch={self.batch_size}, workers={self.parallel_workers})"
        )


@dataclass
class OutputConfig:
    """Output configuration settings.
    
    Attributes:
        format: Output file format
        path: Output directory path
        overwrite: Overwrite existing files
        compression: Compression type
        include_metadata: Include metadata in output
    """
    
    format: OutputFormat = OutputFormat.CSV
    path: str = "./output"
    overwrite: bool = False
    compression: Optional[str] = None
    include_metadata: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        config_dict = asdict(self)
        config_dict['format'] = self.format.value
        return config_dict
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"OutputConfig(format={self.format.value}, path={self.path})"


class ConfigDict(dict):
    """Extended dictionary for configuration management.
    
    Provides convenient access to configuration values with defaults
    and type safety.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize configuration dictionary."""
        super().__init__(*args, **kwargs)
        logger.debug("ConfigDict initialized with %d entries", len(self))
    
    def get_string(self, key: Union[str, ConfigKey], default: str = "") -> str:
        """Get string value with default."""
        key_str = key.value if isinstance(key, ConfigKey) else key
        value = self.get(key_str, default)
        if not isinstance(value, str):
            logger.warning("Expected string for key %s, got %s", key_str, type(value))
        return str(value) if value is not None else default
    
    def get_int(self, key: Union[str, ConfigKey], default: int = 0) -> int:
        """Get integer value with default."""
        key_str = key.value if isinstance(key, ConfigKey) else key
        value = self.get(key_str, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            logger.warning("Could not convert %s to int for key %s", value, key_str)
            return default
    
    def get_float(self, key: Union[str, ConfigKey], default: float = 0.0) -> float:
        """Get float value with default."""
        key_str = key.value if isinstance(key, ConfigKey) else key
        value = self.get(key_str, default)
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            logger.warning("Could not convert %s to float for key %s", value, key_str)
            return default
    
    def get_bool(self, key: Union[str, ConfigKey], default: bool = False) -> bool:
        """Get boolean value with default."""
        key_str = key.value if isinstance(key, ConfigKey) else key
        value = self.get(key_str, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'on')
        return bool(value) if value is not None else default
    
    def get_list(self, key: Union[str, ConfigKey], default: Optional[List] = None) -> List:
        """Get list value with default."""
        key_str = key.value if isinstance(key, ConfigKey) else key
        value = self.get(key_str, default or [])
        return value if isinstance(value, list) else [value]
    
    def get_dict(self, key: Union[str, ConfigKey], default: Optional[Dict] = None) -> Dict:
        """Get dictionary value with default."""
        key_str = key.value if isinstance(key, ConfigKey) else key
        value = self.get(key_str, default or {})
        return value if isinstance(value, dict) else {}
    
    def set_nested(self, key_path: str, value: Any) -> None:
        """Set nested value using dot notation.
        
        Example: set_nested("api.timeout", 60)
        """
        keys = key_path.split('.')
        current = self
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        logger.debug("Set %s = %s", key_path, value)
    
    def get_nested(self, key_path: str, default: Any = None) -> Any:
        """Get nested value using dot notation.
        
        Example: get_nested("api.timeout", 30)
        """
        keys = key_path.split('.')
        current = self
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return default
        return current if current is not None else default
    
    def update_from_dict(self, data: Dict[str, Any], deep: bool = False) -> None:
        """Update configuration from another dictionary.
        
        Args:
            data: Dictionary with configuration updates
            deep: If True, recursively update nested dictionaries
        """
        if deep:
            for key, value in data.items():
                if key in self and isinstance(self[key], dict) and isinstance(value, dict):
                    self[key].update(value)
                else:
                    self[key] = value
        else:
            self.update(data)
        logger.info("Configuration updated with %d entries", len(data))
    
    def to_json(self) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self, indent=2, default=str)
    
    def __str__(self) -> str:
        """String representation."""
        return f"ConfigDict({len(self)} entries)"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        entries = ', '.join(f"{k}: {type(v).__name__}" for k, v in list(self.items())[:3])
        return f"ConfigDict({entries}...)"


class StationsDict(dict):
    """Specialized dictionary for managing weather station configurations.
    
    Provides convenient access to station configurations by ID or index.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize stations dictionary."""
        super().__init__(*args, **kwargs)
        logger.debug("StationsDict initialized with %d stations", len(self))
    
    def add_station(self, station: StationConfig) -> bool:
        """Add a station configuration.
        
        Args:
            station: Station configuration to add
            
        Returns:
            True if added successfully, False if already exists
        """
        if station.station_id in self:
            logger.warning("Station %s already exists", station.station_id)
            return False
        self[station.station_id] = station
        logger.info("Added station: %s", station)
        return True
    
    def get_station(self, station_id: str) -> Optional[StationConfig]:
        """Get station by ID.
        
        Args:
            station_id: Station identifier
            
        Returns:
            Station configuration or None if not found
        """
        return self.get(station_id)
    
    def get_by_name(self, name: str) -> Optional[StationConfig]:
        """Get station by name.
        
        Args:
            name: Station name
            
        Returns:
            Station configuration or None if not found
        """
        for station in self.values():
            if station.name.lower() == name.lower():
                return station
        return None
    
    def get_by_region(self, region: str) -> List[StationConfig]:
        """Get all stations in a region.
        
        Args:
            region: Region name
            
        Returns:
            List of stations in the region
        """
        return [s for s in self.values() if s.region.lower() == region.lower()]
    
    def remove_station(self, station_id: str) -> bool:
        """Remove a station.
        
        Args:
            station_id: Station identifier
            
        Returns:
            True if removed, False if not found
        """
        if station_id in self:
            del self[station_id]
            logger.info("Removed station: %s", station_id)
            return True
        logger.warning("Station %s not found", station_id)
        return False
    
    def list_stations(self) -> List[StationConfig]:
        """Get all stations as list.
        
        Returns:
            List of all station configurations
        """
        return list(self.values())
    
    def list_stations_by_region(self) -> Dict[str, List[StationConfig]]:
        """Get stations organized by region.
        
        Returns:
            Dictionary with regions as keys and station lists as values
        """
        regions = {}
        for station in self.values():
            if station.region not in regions:
                regions[station.region] = []
            regions[station.region].append(station)
        return regions
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert all stations to dictionary list.
        
        Returns:
            List of station dictionaries
        """
        return [station.to_dict() for station in self.values()]
    
    def to_json(self) -> str:
        """Convert to JSON string.
        
        Returns:
            JSON representation of all stations
        """
        return json.dumps(self.to_dict_list(), indent=2, default=str)
    
    def count_by_region(self) -> Dict[str, int]:
        """Count stations by region.
        
        Returns:
            Dictionary with region counts
        """
        counts = {}
        for station in self.values():
            region = station.region or "Unknown"
            counts[region] = counts.get(region, 0) + 1
        return counts
    
    def __str__(self) -> str:
        """String representation."""
        return f"StationsDict({len(self)} stations)"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        regions = len(set(s.region for s in self.values()))
        return f"StationsDict({len(self)} stations, {regions} regions)"


class ConfigurationManager:
    """Central configuration management system.
    
    Manages all configuration dictionaries and provides unified access
    to system settings, station configurations, and extraction parameters.
    """
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config = ConfigDict()
        self.stations = StationsDict()
        self.api_config = None
        self.extraction_config = None
        self.output_config = None
        logger.info("ConfigurationManager initialized")
    
    def load_config(self, data: Dict[str, Any]) -> None:
        """Load configuration from dictionary.
        
        Args:
            data: Configuration dictionary
        """
        self.config.update_from_dict(data, deep=True)
        logger.info("Configuration loaded from dictionary")
    
    def load_from_json(self, json_str: str) -> None:
        """Load configuration from JSON string.
        
        Args:
            json_str: JSON configuration string
        """
        try:
            data = json.loads(json_str)
            self.load_config(data)
            logger.info("Configuration loaded from JSON")
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON: %s", str(e))
            raise
    
    def load_from_file(self, file_path: str) -> None:
        """Load configuration from JSON file.
        
        Args:
            file_path: Path to JSON configuration file
        """
        try:
            with open(file_path, 'r') as f:
                self.load_from_json(f.read())
            logger.info("Configuration loaded from file: %s", file_path)
        except FileNotFoundError:
            logger.error("Configuration file not found: %s", file_path)
            raise
        except Exception as e:
            logger.error("Failed to load configuration: %s", str(e))
            raise
    
    def save_to_file(self, file_path: str) -> None:
        """Save configuration to JSON file.
        
        Args:
            file_path: Path to save JSON configuration
        """
        try:
            with open(file_path, 'w') as f:
                f.write(self.config.to_json())
            logger.info("Configuration saved to file: %s", file_path)
        except Exception as e:
            logger.error("Failed to save configuration: %s", str(e))
            raise
    
    def add_station(self, station: StationConfig) -> bool:
        """Add a station configuration.
        
        Args:
            station: Station configuration to add
            
        Returns:
            True if added successfully
        """
        return self.stations.add_station(station)
    
    def add_stations(self, stations: List[StationConfig]) -> None:
        """Add multiple stations.
        
        Args:
            stations: List of station configurations
        """
        for station in stations:
            self.add_station(station)
        logger.info("Added %d stations", len(stations))
    
    def set_api_config(self, api_config: APIConfig) -> None:
        """Set API configuration.
        
        Args:
            api_config: API configuration object
        """
        self.api_config = api_config
        self.config.update_from_dict({'api': api_config.to_dict()})
        logger.info("API configuration set: %s", api_config)
    
    def set_extraction_config(self, extraction_config: ExtractionConfig) -> None:
        """Set extraction configuration.
        
        Args:
            extraction_config: Extraction configuration object
        """
        self.extraction_config = extraction_config
        self.config.update_from_dict({'extraction': extraction_config.to_dict()})
        logger.info("Extraction configuration set: %s", extraction_config)
    
    def set_output_config(self, output_config: OutputConfig) -> None:
        """Set output configuration.
        
        Args:
            output_config: Output configuration object
        """
        self.output_config = output_config
        self.config.update_from_dict({'output': output_config.to_dict()})
        logger.info("Output configuration set: %s", output_config)
    
    def get_config(self, key: Union[str, ConfigKey], default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        key_str = key.value if isinstance(key, ConfigKey) else key
        return self.config.get(key_str, default)
    
    def get_station(self, station_id: str) -> Optional[StationConfig]:
        """Get station configuration.
        
        Args:
            station_id: Station identifier
            
        Returns:
            Station configuration or None
        """
        return self.stations.get_station(station_id)
    
    def list_all_stations(self) -> List[StationConfig]:
        """Get all stations.
        
        Returns:
            List of all station configurations
        """
        return self.stations.list_stations()
    
    def get_station_count(self) -> int:
        """Get total number of stations.
        
        Returns:
            Number of configured stations
        """
        return len(self.stations)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get configuration statistics.
        
        Returns:
            Dictionary with configuration stats
        """
        return {
            'total_config_keys': len(self.config),
            'total_stations': len(self.stations),
            'regions': len(set(s.region for s in self.stations.values())),
            'api_configured': self.api_config is not None,
            'extraction_configured': self.extraction_config is not None,
            'output_configured': self.output_config is not None,
        }
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"ConfigurationManager(keys={len(self.config)}, "
            f"stations={len(self.stations)})"
        )
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"ConfigurationManager(config={len(self.config)} keys, "
            f"stations={len(self.stations)}, "
            f"api={self.api_config is not None})"
        )
