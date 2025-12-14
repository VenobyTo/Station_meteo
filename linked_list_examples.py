#!/usr/bin/env python
"""Example demonstrating linked list usage for weather station display.

This example shows how to:
1. Create a linked list of weather stations
2. Add stations to the list
3. Display stations sequentially
4. Filter by date range
5. Combine data from multiple stations
"""

import pandas as pd
from datetime import datetime, timezone, timedelta

from projet.linked_list import LinkedList, WeatherStationLinkedList, WeatherStationNode


def example_generic_linked_list():
    """Example 1: Generic linked list operations."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Generic Linked List Operations")
    print("="*60)

    ll = LinkedList()
    
    # Append elements
    print("\nAppending 10, 20, 30...")
    ll.append(10)
    ll.append(20)
    ll.append(30)
    print(f"List: {list(ll)}")
    print(f"Length: {len(ll)}")
    
    # Insert at position
    print("\nInserting 15 at index 1...")
    ll.insert_at(1, 15)
    print(f"List: {list(ll)}")
    
    # Remove element
    print("\nRemoving 20...")
    ll.remove(20)
    print(f"List: {list(ll)}")
    
    # Find element
    print(f"\nFinding 30: index {ll.find(30)}")
    print(f"Contains 15: {ll.contains(15)}")


def example_weather_station_list():
    """Example 2: Weather station linked list."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Weather Station Linked List")
    print("="*60)
    
    # Create sample weather data
    def create_sample_data(start_temp, n_records=5):
        dates = pd.date_range('2024-11-20', periods=n_records, freq='D', tz='UTC')
        temps = [start_temp + i*0.5 for i in range(n_records)]
        return pd.DataFrame({
            'temperature': temps,
            'humidity': range(60, 60 + n_records),
            'pressure': [1013 + i*0.1 for i in range(n_records)]
        }, index=dates)
    
    # Create linked list
    stations_ll = WeatherStationLinkedList()
    
    # Add stations
    print("\nAdding weather stations...")
    stations_ll.add_station('paris_orly', 'Paris Orly', create_sample_data(15))
    stations_ll.add_station('lyon_airport', 'Lyon Airport', create_sample_data(12))
    stations_ll.add_station('toulouse_station', 'Toulouse Station', create_sample_data(14))
    
    print(f"Total stations: {len(stations_ll)}")
    
    # List all stations
    print("\nAll stations in the list:")
    for i, station_str in enumerate(stations_ll.list_stations(), 1):
        print(f"  {i}. {station_str}")
    
    # Access station by ID
    print("\nAccessing station by ID (paris_orly):")
    station = stations_ll.get_station('paris_orly')
    if station:
        print(f"  Name: {station.station_name}")
        print(f"  Records: {len(station.data)}")
        print(station.data)
    
    # Access station by index
    print("\nAccessing station by index (2nd station):")
    station = stations_ll.get_station_by_index(1)
    if station:
        print(f"  Name: {station.station_name}")


def example_iterate_stations():
    """Example 3: Iterating over stations in the linked list."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Iterating Over Stations")
    print("="*60)
    
    def create_sample_data(start_temp, n_records=7):
        dates = pd.date_range('2024-11-15', periods=n_records, freq='D', tz='UTC')
        temps = [start_temp + i*0.3 for i in range(n_records)]
        return pd.DataFrame({
            'temperature': temps,
            'humidity': range(55, 55 + n_records),
            'pressure': [1012 + i*0.05 for i in range(n_records)]
        }, index=dates)
    
    stations_ll = WeatherStationLinkedList()
    stations_ll.add_station('marseille', 'Marseille', create_sample_data(16))
    stations_ll.add_station('nice', 'Nice', create_sample_data(17))
    stations_ll.add_station('antibes', 'Antibes', create_sample_data(16.5))
    
    # Iterate and display each station
    print("\nIterating through stations sequentially:\n")
    for i, station in enumerate(stations_ll, 1):
        print(f"{i}. {station.station_name}")
        print(f"   Temperature range: {station.data['temperature'].min():.1f}°C to {station.data['temperature'].max():.1f}°C")
        print(f"   Average humidity: {station.data['humidity'].mean():.1f}%")
        print()


def example_filter_and_combine():
    """Example 4: Filtering by date and combining data."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Filtering by Date and Combining Data")
    print("="*60)
    
    def create_sample_data(start_temp, n_records=30):
        dates = pd.date_range('2024-10-01', periods=n_records, freq='D', tz='UTC')
        temps = [start_temp + (i % 10)*0.5 for i in range(n_records)]
        return pd.DataFrame({
            'temperature': temps,
            'humidity': range(50, 50 + n_records),
            'pressure': [1010 + (i % 5)*0.1 for i in range(n_records)]
        }, index=dates)
    
    # Create linked list with October-November data
    stations_ll = WeatherStationLinkedList()
    stations_ll.add_station('station_a', 'Station A', create_sample_data(18))
    stations_ll.add_station('station_b', 'Station B', create_sample_data(15))
    
    print(f"\nOriginal stations: {len(stations_ll)} stations")
    print(f"Total records: {len(stations_ll.get_combined_dataframe())}")
    
    # Filter by date range
    print("\nFiltering data from 2024-10-15 to 2024-10-25...")
    filtered_ll = stations_ll.filter_by_date('2024-10-15', '2024-10-25')
    
    print(f"Filtered stations: {len(filtered_ll)} stations")
    for station in filtered_ll.list_stations():
        print(f"  {station}")
    
    # Combine all filtered data
    combined = filtered_ll.get_combined_dataframe()
    print(f"\nCombined filtered data: {len(combined)} records")
    print("\nSample of combined data:")
    print(combined.head())


def example_remove_station():
    """Example 5: Removing stations from the linked list."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Removing Stations from the Linked List")
    print("="*60)
    
    def create_sample_data(start_temp, n_records=5):
        dates = pd.date_range('2024-11-20', periods=n_records, freq='D', tz='UTC')
        return pd.DataFrame({
            'temperature': [start_temp + i*0.5 for i in range(n_records)],
            'humidity': range(60, 60 + n_records)
        }, index=dates)
    
    stations_ll = WeatherStationLinkedList()
    stations_ll.add_station('station_1', 'Station 1', create_sample_data(15))
    stations_ll.add_station('station_2', 'Station 2', create_sample_data(16))
    stations_ll.add_station('station_3', 'Station 3', create_sample_data(14))
    
    print(f"\nInitial stations ({len(stations_ll)}):")
    for station in stations_ll.list_stations():
        print(f"  {station}")
    
    print("\nRemoving 'Station 2'...")
    stations_ll.remove_station('station_2')
    
    print(f"\nRemaining stations ({len(stations_ll)}):")
    for station in stations_ll.list_stations():
        print(f"  {station}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("LINKED LIST WEATHER STATION EXAMPLES")
    print("="*60)
    
    example_generic_linked_list()
    example_weather_station_list()
    example_iterate_stations()
    example_filter_and_combine()
    example_remove_station()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
