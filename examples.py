#!/usr/bin/env python
"""Example script demonstrating weather data retrieval from Meteostat API.

This script shows how to:
1. Search for weather stations
2. Fetch historical data for a specific station
3. Fetch data for the nearest station to coordinates
4. Clean and analyze the retrieved data
"""

import logging
from datetime import datetime, timedelta

from projet import MeteostatDataRetriever, DataCleaner, CSVDataRetriever

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def example_search_stations():
    """Example 1: Search for weather stations."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Search for Weather Stations")
    print("=" * 60)

    retriever = MeteostatDataRetriever()

    # Search for stations in France
    print("\nSearching for stations in France...")
    stations = retriever.search_stations(country="FR")
    print(f"Found {len(stations)} stations in France")
    print(stations.head(10))


def example_fetch_by_station():
    """Example 2: Fetch data for a specific station."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Fetch Data for Paris Orly Station")
    print("=" * 60)

    retriever = MeteostatDataRetriever()

    # Paris Orly station (ICAO: LFPO)
    station_id = "10438"

    print(f"\nFetching data for station {station_id}...")
    print("Time period: Last 30 days")

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    try:
        df = retriever.fetch_by_station(
            station_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )

        print(f"\nRetrieved {len(df)} records")
        print("\nFirst 5 rows:")
        print(df.head())
        print("\nStatistics:")
        print(df.describe())

    except Exception as e:
        logger.error("Failed to fetch data: %s", e)


def example_fetch_by_coordinates():
    """Example 3: Fetch data for nearest station to coordinates."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Fetch Data by Coordinates")
    print("=" * 60)

    retriever = MeteostatDataRetriever()

    # Paris coordinates
    latitude = 48.8566
    longitude = 2.3522

    print(f"\nFetching data for nearest station to ({latitude}, {longitude})")
    print("Time period: Last 7 days")
    print("Search radius: 25 km")

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    try:
        df = retriever.fetch_by_coordinates(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            radius_km=25,
        )

        print(f"\nRetrieved {len(df)} records")
        print("\nData sample:")
        print(df.head())

    except Exception as e:
        logger.error("Failed to fetch data: %s", e)


def example_compare_csv_and_api():
    """Example 4: Compare CSV and API data retrieval."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Compare CSV vs API Retrieval")
    print("=" * 60)

    # Load from CSV (local file)
    print("\n--- CSV Retrieval ---")
    csv_retriever = CSVDataRetriever(DataCleaner())
    try:
        csv_path = "42-station-meteo-toulouse-parc-compans-cafarelli.csv"
        df_csv = csv_retriever.fetch(csv_path)
        print(f"✓ Loaded {len(df_csv)} records from CSV")
        print(f"  Columns: {list(df_csv.columns)}")
    except FileNotFoundError:
        print(f"✗ CSV file not found: {csv_path}")

    # Fetch from API (live data)
    print("\n--- API Retrieval ---")
    api_retriever = MeteostatDataRetriever()
    try:
        df_api = api_retriever.fetch_by_station(
            "10438",  # Paris
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        print(f"✓ Fetched {len(df_api)} records from API")
        print(f"  Columns: {list(df_api.columns)}")
    except Exception as e:
        print(f"✗ API fetch failed: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("WEATHER DATA RETRIEVAL EXAMPLES")
    print("=" * 60)

    try:
        example_search_stations()
    except Exception as e:
        logger.error("Example 1 failed: %s", e)

    try:
        example_fetch_by_station()
    except Exception as e:
        logger.error("Example 2 failed: %s", e)

    try:
        example_fetch_by_coordinates()
    except Exception as e:
        logger.error("Example 3 failed: %s", e)

    try:
        example_compare_csv_and_api()
    except Exception as e:
        logger.error("Example 4 failed: %s", e)

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
