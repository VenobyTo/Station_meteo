"""Tests for configuration module."""

import pytest
import json
import tempfile
from pathlib import Path

from projet.config import (
    ConfigDict, StationsDict, ConfigurationManager,
    StationConfig, APIConfig, ExtractionConfig, OutputConfig,
    ConfigKey, DataSource, OutputFormat
)


class TestConfigDict:
    """Tests for ConfigDict."""
    
    def test_config_dict_creation(self):
        """Test ConfigDict creation."""
        config = ConfigDict()
        assert len(config) == 0
        assert isinstance(config, dict)
    
    def test_config_dict_with_initial_data(self):
        """Test ConfigDict with initial data."""
        data = {'key1': 'value1', 'key2': 'value2'}
        config = ConfigDict(data)
        assert len(config) == 2
        assert config['key1'] == 'value1'
    
    def test_get_string(self):
        """Test getting string values."""
        config = ConfigDict({'name': 'Paris', 'city': 'Lyon'})
        assert config.get_string('name') == 'Paris'
        assert config.get_string('missing', 'default') == 'default'
        assert config.get_string('city') == 'Lyon'
    
    def test_get_int(self):
        """Test getting integer values."""
        config = ConfigDict({'timeout': 30, 'retries': '5'})
        assert config.get_int('timeout') == 30
        assert config.get_int('retries') == 5
        assert config.get_int('missing', 10) == 10
    
    def test_get_float(self):
        """Test getting float values."""
        config = ConfigDict({'rate': 10.5, 'limit': '25.0'})
        assert config.get_float('rate') == 10.5
        assert config.get_float('limit') == 25.0
        assert config.get_float('missing', 1.0) == 1.0
    
    def test_get_bool(self):
        """Test getting boolean values."""
        config = ConfigDict({'flag1': True, 'flag2': 'yes', 'flag3': '1'})
        assert config.get_bool('flag1') is True
        assert config.get_bool('flag2') is True
        assert config.get_bool('flag3') is True
        assert config.get_bool('missing', False) is False
    
    def test_get_list(self):
        """Test getting list values."""
        config = ConfigDict({'items': [1, 2, 3]})
        assert config.get_list('items') == [1, 2, 3]
        assert config.get_list('missing') == []
    
    def test_get_dict(self):
        """Test getting dict values."""
        config = ConfigDict({'nested': {'a': 1, 'b': 2}})
        assert config.get_dict('nested') == {'a': 1, 'b': 2}
        assert config.get_dict('missing') == {}
    
    def test_set_nested(self):
        """Test setting nested values."""
        config = ConfigDict()
        config.set_nested('api.url', 'http://example.com')
        config.set_nested('api.timeout', 30)
        
        assert config['api']['url'] == 'http://example.com'
        assert config['api']['timeout'] == 30
    
    def test_get_nested(self):
        """Test getting nested values."""
        config = ConfigDict({'api': {'url': 'http://api.example.com', 'key': 'secret'}})
        assert config.get_nested('api.url') == 'http://api.example.com'
        assert config.get_nested('api.key') == 'secret'
        assert config.get_nested('api.missing', 'default') == 'default'
    
    def test_update_from_dict(self):
        """Test updating from another dict."""
        config = ConfigDict({'a': 1, 'b': 2})
        config.update_from_dict({'c': 3, 'd': 4})
        
        assert len(config) == 4
        assert config['c'] == 3
    
    def test_to_json(self):
        """Test JSON serialization."""
        config = ConfigDict({'name': 'Test', 'value': 42})
        json_str = config.to_json()
        
        data = json.loads(json_str)
        assert data['name'] == 'Test'
        assert data['value'] == 42


class TestStationsDict:
    """Tests for StationsDict."""
    
    def test_stations_dict_creation(self):
        """Test StationsDict creation."""
        stations = StationsDict()
        assert len(stations) == 0
        assert isinstance(stations, dict)
    
    def test_add_station(self):
        """Test adding station."""
        stations = StationsDict()
        station = StationConfig('PARIS_01', 'Paris', 48.856, 2.352)
        
        result = stations.add_station(station)
        assert result is True
        assert len(stations) == 1
        assert stations['PARIS_01'] == station
    
    def test_add_duplicate_station(self):
        """Test adding duplicate station."""
        stations = StationsDict()
        station = StationConfig('PARIS_01', 'Paris', 48.856, 2.352)
        
        assert stations.add_station(station) is True
        assert stations.add_station(station) is False
    
    def test_get_station(self):
        """Test getting station by ID."""
        stations = StationsDict()
        station = StationConfig('PARIS_01', 'Paris', 48.856, 2.352)
        stations.add_station(station)
        
        retrieved = stations.get_station('PARIS_01')
        assert retrieved == station
        assert stations.get_station('MISSING') is None
    
    def test_get_by_name(self):
        """Test getting station by name."""
        stations = StationsDict()
        station = StationConfig('PARIS_01', 'Paris', 48.856, 2.352)
        stations.add_station(station)
        
        retrieved = stations.get_by_name('Paris')
        assert retrieved == station
        assert stations.get_by_name('Missing') is None
    
    def test_get_by_region(self):
        """Test getting stations by region."""
        stations = StationsDict()
        s1 = StationConfig('P1', 'Paris 1', region='IDF')
        s2 = StationConfig('P2', 'Paris 2', region='IDF')
        s3 = StationConfig('L1', 'Lyon 1', region='ARA')
        
        stations.add_station(s1)
        stations.add_station(s2)
        stations.add_station(s3)
        
        idf_stations = stations.get_by_region('IDF')
        assert len(idf_stations) == 2
        
        ara_stations = stations.get_by_region('ARA')
        assert len(ara_stations) == 1
    
    def test_remove_station(self):
        """Test removing station."""
        stations = StationsDict()
        station = StationConfig('PARIS_01', 'Paris')
        stations.add_station(station)
        
        assert stations.remove_station('PARIS_01') is True
        assert len(stations) == 0
        assert stations.remove_station('PARIS_01') is False
    
    def test_list_stations(self):
        """Test listing all stations."""
        stations = StationsDict()
        s1 = StationConfig('S1', 'Station 1')
        s2 = StationConfig('S2', 'Station 2')
        
        stations.add_station(s1)
        stations.add_station(s2)
        
        all_stations = stations.list_stations()
        assert len(all_stations) == 2
    
    def test_list_stations_by_region(self):
        """Test organizing stations by region."""
        stations = StationsDict()
        s1 = StationConfig('P1', 'Paris', region='IDF')
        s2 = StationConfig('L1', 'Lyon', region='ARA')
        s3 = StationConfig('P2', 'Paris 2', region='IDF')
        
        for s in [s1, s2, s3]:
            stations.add_station(s)
        
        by_region = stations.list_stations_by_region()
        assert len(by_region) == 2
        assert len(by_region['IDF']) == 2
        assert len(by_region['ARA']) == 1
    
    def test_to_dict_list(self):
        """Test converting to dict list."""
        stations = StationsDict()
        s1 = StationConfig('S1', 'Station 1')
        s2 = StationConfig('S2', 'Station 2')
        
        stations.add_station(s1)
        stations.add_station(s2)
        
        dicts = stations.to_dict_list()
        assert len(dicts) == 2
        assert dicts[0]['station_id'] == 'S1'
    
    def test_count_by_region(self):
        """Test counting stations by region."""
        stations = StationsDict()
        stations.add_station(StationConfig('P1', 'Paris 1', region='IDF'))
        stations.add_station(StationConfig('P2', 'Paris 2', region='IDF'))
        stations.add_station(StationConfig('L1', 'Lyon', region='ARA'))
        
        counts = stations.count_by_region()
        assert counts['IDF'] == 2
        assert counts['ARA'] == 1


class TestStationConfig:
    """Tests for StationConfig."""
    
    def test_station_config_creation(self):
        """Test StationConfig creation."""
        station = StationConfig('PARIS_01', 'Paris', 48.856, 2.352)
        assert station.station_id == 'PARIS_01'
        assert station.name == 'Paris'
        assert station.latitude == 48.856
        assert station.longitude == 2.352
    
    def test_station_config_to_dict(self):
        """Test converting to dictionary."""
        station = StationConfig('PARIS_01', 'Paris', 48.856, 2.352, region='IDF')
        station_dict = station.to_dict()
        
        assert station_dict['station_id'] == 'PARIS_01'
        assert station_dict['name'] == 'Paris'
        assert station_dict['region'] == 'IDF'


class TestAPIConfig:
    """Tests for APIConfig."""
    
    def test_api_config_creation(self):
        """Test APIConfig creation."""
        api = APIConfig('http://api.example.com', api_key='secret')
        assert api.base_url == 'http://api.example.com'
        assert api.api_key == 'secret'
        assert api.timeout == 30
    
    def test_api_config_to_dict(self):
        """Test converting to dictionary."""
        api = APIConfig('http://api.example.com', timeout=60)
        api_dict = api.to_dict()
        
        assert api_dict['base_url'] == 'http://api.example.com'
        assert api_dict['timeout'] == 60


class TestExtractionConfig:
    """Tests for ExtractionConfig."""
    
    def test_extraction_config_creation(self):
        """Test ExtractionConfig creation."""
        config = ExtractionConfig(source=DataSource.TOULOUSE, batch_size=50)
        assert config.source == DataSource.TOULOUSE
        assert config.batch_size == 50
    
    def test_extraction_config_to_dict(self):
        """Test converting to dictionary."""
        config = ExtractionConfig(source=DataSource.METEOSTAT)
        config_dict = config.to_dict()
        
        assert config_dict['source'] == 'meteostat'


class TestOutputConfig:
    """Tests for OutputConfig."""
    
    def test_output_config_creation(self):
        """Test OutputConfig creation."""
        config = OutputConfig(format=OutputFormat.JSON, path='/data/output')
        assert config.format == OutputFormat.JSON
        assert config.path == '/data/output'
    
    def test_output_config_to_dict(self):
        """Test converting to dictionary."""
        config = OutputConfig(format=OutputFormat.CSV)
        config_dict = config.to_dict()
        
        assert config_dict['format'] == 'csv'


class TestConfigurationManager:
    """Tests for ConfigurationManager."""
    
    def test_manager_creation(self):
        """Test ConfigurationManager creation."""
        manager = ConfigurationManager()
        assert len(manager.config) == 0
        assert len(manager.stations) == 0
    
    def test_load_config(self):
        """Test loading configuration."""
        manager = ConfigurationManager()
        data = {'api_url': 'http://api.example.com', 'timeout': 30}
        manager.load_config(data)
        
        assert manager.config['api_url'] == 'http://api.example.com'
        assert manager.config['timeout'] == 30
    
    def test_add_station(self):
        """Test adding station."""
        manager = ConfigurationManager()
        station = StationConfig('PARIS_01', 'Paris')
        
        result = manager.add_station(station)
        assert result is True
        assert manager.get_station_count() == 1
    
    def test_add_multiple_stations(self):
        """Test adding multiple stations."""
        manager = ConfigurationManager()
        stations = [
            StationConfig('S1', 'Station 1'),
            StationConfig('S2', 'Station 2'),
            StationConfig('S3', 'Station 3'),
        ]
        
        manager.add_stations(stations)
        assert manager.get_station_count() == 3
    
    def test_set_api_config(self):
        """Test setting API configuration."""
        manager = ConfigurationManager()
        api = APIConfig('http://api.example.com')
        
        manager.set_api_config(api)
        assert manager.api_config == api
        assert 'api' in manager.config
    
    def test_set_extraction_config(self):
        """Test setting extraction configuration."""
        manager = ConfigurationManager()
        extraction = ExtractionConfig(batch_size=100)
        
        manager.set_extraction_config(extraction)
        assert manager.extraction_config == extraction
    
    def test_set_output_config(self):
        """Test setting output configuration."""
        manager = ConfigurationManager()
        output = OutputConfig(path='/data/output')
        
        manager.set_output_config(output)
        assert manager.output_config == output
    
    def test_get_station(self):
        """Test getting station."""
        manager = ConfigurationManager()
        station = StationConfig('PARIS_01', 'Paris')
        manager.add_station(station)
        
        retrieved = manager.get_station('PARIS_01')
        assert retrieved == station
    
    def test_list_all_stations(self):
        """Test listing all stations."""
        manager = ConfigurationManager()
        s1 = StationConfig('S1', 'Station 1')
        s2 = StationConfig('S2', 'Station 2')
        
        manager.add_stations([s1, s2])
        
        stations = manager.list_all_stations()
        assert len(stations) == 2
    
    def test_get_stats(self):
        """Test getting statistics."""
        manager = ConfigurationManager()
        manager.load_config({'key1': 'value1'})
        manager.add_station(StationConfig('S1', 'Station 1'))
        
        stats = manager.get_stats()
        assert stats['total_config_keys'] > 0
        assert stats['total_stations'] == 1
    
    def test_load_from_json(self):
        """Test loading from JSON string."""
        manager = ConfigurationManager()
        json_str = '{"api_url": "http://api.example.com", "timeout": 30}'
        
        manager.load_from_json(json_str)
        assert manager.config['api_url'] == 'http://api.example.com'
    
    def test_load_from_file(self):
        """Test loading from file."""
        manager = ConfigurationManager()
        config_data = {'api_url': 'http://api.example.com', 'timeout': 60}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            manager.load_from_file(temp_path)
            assert manager.config['api_url'] == 'http://api.example.com'
            assert manager.config['timeout'] == 60
        finally:
            Path(temp_path).unlink()
    
    def test_save_to_file(self):
        """Test saving to file."""
        manager = ConfigurationManager()
        manager.load_config({'api_url': 'http://api.example.com'})
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            manager.save_to_file(temp_path)
            
            # Verify saved content
            with open(temp_path, 'r') as f:
                data = json.load(f)
            assert data['api_url'] == 'http://api.example.com'
        finally:
            Path(temp_path).unlink()
