"""Unit tests for linked list implementation."""

import pytest
import pandas as pd
from datetime import datetime, timezone, timedelta

from projet.linked_list import LinkedList, WeatherStationNode, WeatherStationLinkedList


class TestLinkedList:
    """Tests for the generic LinkedList class."""

    def test_empty_list(self):
        """Test creating an empty linked list."""
        ll = LinkedList()
        assert len(ll) == 0
        assert ll.head is None
        assert list(ll) == []

    def test_append_single_element(self):
        """Test appending a single element."""
        ll = LinkedList()
        ll.append(10)
        assert len(ll) == 1
        assert ll.head.data == 10
        assert list(ll) == [10]

    def test_append_multiple_elements(self):
        """Test appending multiple elements."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert len(ll) == 3
        assert list(ll) == [1, 2, 3]

    def test_prepend_single_element(self):
        """Test prepending a single element."""
        ll = LinkedList()
        ll.prepend(10)
        assert len(ll) == 1
        assert ll.head.data == 10

    def test_prepend_multiple_elements(self):
        """Test prepending multiple elements."""
        ll = LinkedList()
        ll.append(2)
        ll.append(3)
        ll.prepend(1)
        assert list(ll) == [1, 2, 3]

    def test_insert_at_beginning(self):
        """Test inserting at the beginning."""
        ll = LinkedList()
        ll.append(1)
        ll.append(3)
        ll.insert_at(1, 2)
        assert list(ll) == [1, 2, 3]

    def test_insert_at_middle(self):
        """Test inserting in the middle."""
        ll = LinkedList()
        ll.append(1)
        ll.append(3)
        ll.insert_at(1, 2)
        assert list(ll) == [1, 2, 3]

    def test_insert_at_end(self):
        """Test inserting at the end."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.insert_at(2, 3)
        assert list(ll) == [1, 2, 3]

    def test_insert_at_invalid_index(self):
        """Test inserting at invalid index raises error."""
        ll = LinkedList()
        ll.append(1)
        with pytest.raises(IndexError):
            ll.insert_at(5, 10)

    def test_remove_existing_element(self):
        """Test removing an existing element."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert ll.remove(2) is True
        assert list(ll) == [1, 3]
        assert len(ll) == 2

    def test_remove_nonexistent_element(self):
        """Test removing a nonexistent element returns False."""
        ll = LinkedList()
        ll.append(1)
        assert ll.remove(5) is False
        assert len(ll) == 1

    def test_remove_head_element(self):
        """Test removing the head element."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        assert ll.remove(1) is True
        assert list(ll) == [2]

    def test_remove_at_index(self):
        """Test removing element at specific index."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        removed = ll.remove_at(1)
        assert removed == 2
        assert list(ll) == [1, 3]

    def test_remove_at_invalid_index(self):
        """Test removing at invalid index raises error."""
        ll = LinkedList()
        ll.append(1)
        with pytest.raises(IndexError):
            ll.remove_at(5)

    def test_get_at_index(self):
        """Test getting element at specific index."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert ll.get_at(0) == 1
        assert ll.get_at(1) == 2
        assert ll.get_at(2) == 3

    def test_get_at_invalid_index(self):
        """Test getting at invalid index returns None."""
        ll = LinkedList()
        ll.append(1)
        assert ll.get_at(5) is None
        assert ll.get_at(-1) is None

    def test_find_existing_element(self):
        """Test finding an existing element."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert ll.find(1) == 0
        assert ll.find(2) == 1
        assert ll.find(3) == 2

    def test_find_nonexistent_element(self):
        """Test finding nonexistent element returns -1."""
        ll = LinkedList()
        ll.append(1)
        assert ll.find(5) == -1

    def test_contains_existing_element(self):
        """Test checking if element exists."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        assert ll.contains(1) is True
        assert ll.contains(2) is True

    def test_contains_nonexistent_element(self):
        """Test checking if nonexistent element returns False."""
        ll = LinkedList()
        ll.append(1)
        assert ll.contains(5) is False

    def test_clear_list(self):
        """Test clearing the list."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        ll.clear()
        assert len(ll) == 0
        assert ll.head is None
        assert list(ll) == []

    def test_iteration(self):
        """Test iterating over the list."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        result = [x for x in ll]
        assert result == [1, 2, 3]

    def test_string_representation(self):
        """Test string representation of the list."""
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert "1" in str(ll)
        assert "2" in str(ll)
        assert "3" in str(ll)


class TestWeatherStationNode:
    """Tests for WeatherStationNode class."""

    def test_create_node(self):
        """Test creating a weather station node."""
        df = pd.DataFrame({'temp': [20, 21, 22]})
        node = WeatherStationNode('station1', 'Paris', df)
        assert node.station_id == 'station1'
        assert node.station_name == 'Paris'
        assert len(node.data) == 3

    def test_node_equality(self):
        """Test node equality based on station ID."""
        df1 = pd.DataFrame({'temp': [20]})
        df2 = pd.DataFrame({'temp': [21]})
        node1 = WeatherStationNode('station1', 'Paris', df1)
        node2 = WeatherStationNode('station1', 'Lyon', df2)
        assert node1 == node2  # Same ID

    def test_node_inequality(self):
        """Test node inequality with different station IDs."""
        df = pd.DataFrame({'temp': [20]})
        node1 = WeatherStationNode('station1', 'Paris', df)
        node2 = WeatherStationNode('station2', 'Paris', df)
        assert node1 != node2

    def test_node_string_representation(self):
        """Test string representation of node."""
        df = pd.DataFrame({'temp': [20, 21]})
        node = WeatherStationNode('station1', 'Paris', df)
        str_repr = str(node)
        assert 'Paris' in str_repr
        assert 'station1' in str_repr
        assert '2' in str_repr  # 2 observations

    def test_display_summary_with_data(self):
        """Test displaying summary with data."""
        dates = pd.date_range('2024-01-01', periods=5, tz='UTC')
        df = pd.DataFrame({'temp': [20, 21, 22, 23, 24]}, index=dates)
        node = WeatherStationNode('station1', 'Paris', df)
        summary = node.display_summary()
        assert 'Paris' in summary
        assert 'station1' in summary
        assert '5' in summary  # 5 records

    def test_display_summary_empty_data(self):
        """Test displaying summary with empty data."""
        df = pd.DataFrame()
        node = WeatherStationNode('station1', 'Paris', df)
        summary = node.display_summary()
        assert 'No data available' in summary


class TestWeatherStationLinkedList:
    """Tests for WeatherStationLinkedList class."""

    def create_sample_dataframe(self, n_records=10):
        """Helper to create sample weather data."""
        dates = pd.date_range('2024-01-01', periods=n_records, tz='UTC')
        return pd.DataFrame({
            'temperature': range(20, 20 + n_records),
            'humidity': range(60, 60 + n_records),
            'pressure': [1013] * n_records
        }, index=dates)

    def test_empty_weather_list(self):
        """Test creating an empty weather station list."""
        wsl = WeatherStationLinkedList()
        assert len(wsl) == 0
        assert list(wsl.list_stations()) == []

    def test_add_single_station(self):
        """Test adding a single station."""
        wsl = WeatherStationLinkedList()
        df = self.create_sample_dataframe(5)
        wsl.add_station('station1', 'Paris', df)
        assert len(wsl) == 1
        assert wsl.get_station('station1') is not None

    def test_add_multiple_stations(self):
        """Test adding multiple stations."""
        wsl = WeatherStationLinkedList()
        df1 = self.create_sample_dataframe(5)
        df2 = self.create_sample_dataframe(3)
        wsl.add_station('station1', 'Paris', df1)
        wsl.add_station('station2', 'Lyon', df2)
        assert len(wsl) == 2

    def test_remove_station(self):
        """Test removing a station."""
        wsl = WeatherStationLinkedList()
        df = self.create_sample_dataframe(5)
        wsl.add_station('station1', 'Paris', df)
        assert wsl.remove_station('station1') is True
        assert len(wsl) == 0

    def test_remove_nonexistent_station(self):
        """Test removing nonexistent station returns False."""
        wsl = WeatherStationLinkedList()
        assert wsl.remove_station('nonexistent') is False

    def test_get_station_by_id(self):
        """Test retrieving station by ID."""
        wsl = WeatherStationLinkedList()
        df = self.create_sample_dataframe(5)
        wsl.add_station('station1', 'Paris', df)
        station = wsl.get_station('station1')
        assert station is not None
        assert station.station_id == 'station1'
        assert station.station_name == 'Paris'

    def test_get_station_nonexistent(self):
        """Test retrieving nonexistent station returns None."""
        wsl = WeatherStationLinkedList()
        assert wsl.get_station('nonexistent') is None

    def test_get_station_by_index(self):
        """Test retrieving station by index."""
        wsl = WeatherStationLinkedList()
        df1 = self.create_sample_dataframe(5)
        df2 = self.create_sample_dataframe(5)
        wsl.add_station('station1', 'Paris', df1)
        wsl.add_station('station2', 'Lyon', df2)
        station = wsl.get_station_by_index(0)
        assert station.station_id == 'station1'
        station = wsl.get_station_by_index(1)
        assert station.station_id == 'station2'

    def test_get_station_by_invalid_index(self):
        """Test retrieving station by invalid index returns None."""
        wsl = WeatherStationLinkedList()
        df = self.create_sample_dataframe(5)
        wsl.add_station('station1', 'Paris', df)
        assert wsl.get_station_by_index(5) is None

    def test_list_stations(self):
        """Test listing all stations."""
        wsl = WeatherStationLinkedList()
        df1 = self.create_sample_dataframe(5)
        df2 = self.create_sample_dataframe(3)
        wsl.add_station('station1', 'Paris', df1)
        wsl.add_station('station2', 'Lyon', df2)
        stations = wsl.list_stations()
        assert len(stations) == 2
        assert any('Paris' in s for s in stations)
        assert any('Lyon' in s for s in stations)

    def test_combined_dataframe(self):
        """Test combining all station data into one DataFrame."""
        wsl = WeatherStationLinkedList()
        df1 = self.create_sample_dataframe(5)
        df2 = self.create_sample_dataframe(3)
        wsl.add_station('station1', 'Paris', df1)
        wsl.add_station('station2', 'Lyon', df2)
        combined = wsl.get_combined_dataframe()
        assert len(combined) == 8
        assert 'station_id' in combined.columns
        assert 'station_name' in combined.columns

    def test_combined_dataframe_empty_list(self):
        """Test combined DataFrame from empty list."""
        wsl = WeatherStationLinkedList()
        combined = wsl.get_combined_dataframe()
        assert combined.empty

    def test_filter_by_date(self):
        """Test filtering stations by date range."""
        wsl = WeatherStationLinkedList()
        dates = pd.date_range('2024-01-01', periods=10, tz='UTC')
        df = pd.DataFrame({
            'temperature': range(20, 30),
            'humidity': range(60, 70)
        }, index=dates)
        wsl.add_station('station1', 'Paris', df)
        
        filtered = wsl.filter_by_date('2024-01-03', '2024-01-07')
        assert len(filtered) == 1
        filtered_data = filtered.get_station('station1').data
        assert len(filtered_data) == 5

    def test_filter_by_date_no_match(self):
        """Test filtering with date range that has no data."""
        wsl = WeatherStationLinkedList()
        dates = pd.date_range('2024-01-01', periods=5, tz='UTC')
        df = pd.DataFrame({'temperature': range(20, 25)}, index=dates)
        wsl.add_station('station1', 'Paris', df)
        
        filtered = wsl.filter_by_date('2024-12-01', '2024-12-31')
        assert len(filtered) == 0

    def test_iteration(self):
        """Test iterating over stations."""
        wsl = WeatherStationLinkedList()
        df1 = self.create_sample_dataframe(5)
        df2 = self.create_sample_dataframe(5)
        wsl.add_station('station1', 'Paris', df1)
        wsl.add_station('station2', 'Lyon', df2)
        
        stations = list(wsl)
        assert len(stations) == 2
        assert stations[0].station_name == 'Paris'
        assert stations[1].station_name == 'Lyon'

    def test_string_representation(self):
        """Test string representation of weather station list."""
        wsl = WeatherStationLinkedList()
        df = self.create_sample_dataframe(5)
        wsl.add_station('station1', 'Paris', df)
        repr_str = repr(wsl)
        assert '1' in repr_str  # 1 station
