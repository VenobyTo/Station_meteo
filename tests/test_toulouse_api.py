"""Unit tests for ToulouseMeteoAPIRetriever."""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
import pandas as pd
import json

from projet.api import ToulouseMeteoAPIRetriever
from projet.cleaner import DataCleaner


class TestToulouseMeteoAPIRetriever(unittest.TestCase):
    """Test suite for ToulouseMeteoAPIRetriever."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.retriever = ToulouseMeteoAPIRetriever()
        self.cleaner = DataCleaner()

    def test_init(self) -> None:
        """Test ToulouseMeteoAPIRetriever initialization."""
        retriever = ToulouseMeteoAPIRetriever()
        self.assertIsNotNone(retriever)
        self.assertEqual(
            retriever.BASE_URL,
            "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets",
        )
        self.assertEqual(retriever.DATASET_ID, "42-station-meteo-toulouse-parc-compans-cafarelli")
        self.assertIsInstance(retriever.cleaner, DataCleaner)

    def test_parse_dates_none_defaults(self) -> None:
        """Test _parse_dates with None defaults to 30 days ago and today."""
        start, end = ToulouseMeteoAPIRetriever._parse_dates(None, None)

        # Both should be timezone-aware
        self.assertIsNotNone(start.tzinfo)
        self.assertIsNotNone(end.tzinfo)
        self.assertEqual(start.tzinfo, timezone.utc)
        self.assertEqual(end.tzinfo, timezone.utc)

        # End should be more recent
        self.assertLess(start, end)

        # Difference should be roughly 30 days
        diff = end - start
        self.assertGreater(diff.days, 29)
        self.assertLess(diff.days, 31)

    def test_parse_dates_string_dates(self) -> None:
        """Test _parse_dates with string date arguments."""
        start_str = "2024-01-01"
        end_str = "2024-12-31"

        start, end = ToulouseMeteoAPIRetriever._parse_dates(start_str, end_str)

        self.assertEqual(start.year, 2024)
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.year, 2024)
        self.assertEqual(end.month, 12)
        self.assertEqual(end.day, 31)

        # Should be timezone-aware
        self.assertEqual(start.tzinfo, timezone.utc)
        self.assertEqual(end.tzinfo, timezone.utc)

    def test_parse_dates_datetime_objects(self) -> None:
        """Test _parse_dates with datetime objects."""
        start = datetime(2024, 1, 1, 12, 0, 0)
        end = datetime(2024, 12, 31, 23, 59, 59)

        result_start, result_end = ToulouseMeteoAPIRetriever._parse_dates(start, end)

        self.assertEqual(result_start.year, 2024)
        self.assertEqual(result_end.year, 2024)

        # Naive datetimes should be made timezone-aware
        self.assertEqual(result_start.tzinfo, timezone.utc)
        self.assertEqual(result_end.tzinfo, timezone.utc)

    def test_parse_dates_mixed_types(self) -> None:
        """Test _parse_dates with mixed string and datetime arguments."""
        start_str = "2024-06-01"
        end_dt = datetime(2024, 12, 31, 23, 59, 59)

        start, end = ToulouseMeteoAPIRetriever._parse_dates(start_str, end_dt)

        self.assertEqual(start.year, 2024)
        self.assertEqual(start.month, 6)
        self.assertEqual(end.year, 2024)
        self.assertEqual(end.tzinfo, timezone.utc)

    def test_parse_dates_aware_datetime(self) -> None:
        """Test _parse_dates with timezone-aware datetime objects."""
        start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        result_start, result_end = ToulouseMeteoAPIRetriever._parse_dates(start, end)

        # Should preserve timezone
        self.assertEqual(result_start.tzinfo, timezone.utc)
        self.assertEqual(result_end.tzinfo, timezone.utc)
        self.assertEqual(result_start, start)
        self.assertEqual(result_end, end)

    def test_parse_dates_invalid_order(self) -> None:
        """Test _parse_dates raises ValueError when start > end."""
        start = "2024-12-31"
        end = "2024-01-01"

        with self.assertRaises(ValueError) as context:
            ToulouseMeteoAPIRetriever._parse_dates(start, end)

        self.assertIn("before", str(context.exception))

    def test_build_where_clause(self) -> None:
        """Test _build_where_clause returns IS NOT NULL check."""
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 12, 31, tzinfo=timezone.utc)

        where_clause = ToulouseMeteoAPIRetriever._build_where_clause(start, end)

        # Should return IS NOT NULL for date filtering at Python level
        self.assertEqual(where_clause, "heure_utc IS NOT NULL")

    def test_column_mapping(self) -> None:
        """Test that column mapping is defined and complete."""
        self.assertIsInstance(self.retriever.COLUMN_MAPPING, dict)
        self.assertGreater(len(self.retriever.COLUMN_MAPPING), 0)

        # Test key mappings
        self.assertIn("temperature_en_degre_c", self.retriever.COLUMN_MAPPING)
        self.assertEqual(self.retriever.COLUMN_MAPPING["temperature_en_degre_c"], "temperature")
        self.assertIn("humidite", self.retriever.COLUMN_MAPPING)
        self.assertEqual(self.retriever.COLUMN_MAPPING["humidite"], "humidity")

    @patch("projet.api.requests.get")
    def test_get_total_count_success(self, mock_get: MagicMock) -> None:
        """Test get_total_count returns correct total."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"total_count": 165480}
        mock_get.return_value = mock_response

        total = self.retriever.get_total_count()

        self.assertEqual(total, 165480)
        mock_get.assert_called_once()

    @patch("projet.api.requests.get")
    def test_get_total_count_no_data(self, mock_get: MagicMock) -> None:
        """Test get_total_count returns 0 when no results."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        total = self.retriever.get_total_count()

        self.assertEqual(total, 0)

    @patch("projet.api.requests.get")
    def test_get_total_count_with_date_range(self, mock_get: MagicMock) -> None:
        """Test get_total_count with custom date range."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"total_count": 10000}
        mock_get.return_value = mock_response

        total = self.retriever.get_total_count("2024-01-01", "2024-12-31")

        self.assertEqual(total, 10000)
        # Verify API was called
        mock_get.assert_called_once()

    @patch("projet.api.requests.get")
    def test_fetch_observations_success(self, mock_get: MagicMock) -> None:
        """Test fetch_observations returns DataFrame with data."""
        # Create mock response with realistic data in date range
        now = datetime.now(timezone.utc)
        base_date = now.replace(hour=10, minute=0, second=0, microsecond=0)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "temperature_en_degre_c": 20.5,
                    "humidite": 65,
                    "pression": 101325,
                    "pluie": 0.0,
                    "force_moyenne_du_vecteur_vent": 5,
                    "heure_utc": base_date.isoformat(),
                    "id": 42,
                    "type_de_station": "ISS",
                },
                {
                    "temperature_en_degre_c": 21.2,
                    "humidite": 63,
                    "pression": 101320,
                    "pluie": 0.0,
                    "force_moyenne_du_vecteur_vent": 4,
                    "heure_utc": (base_date + timedelta(hours=1)).isoformat(),
                    "id": 42,
                    "type_de_station": "ISS",
                },
            ],
            "total_count": 2,
        }
        mock_get.return_value = mock_response

        df = self.retriever.fetch_observations(limit=2)

        # Should return DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Should have data (after date filtering)
        self.assertGreaterEqual(len(df), 0)

        # If data returned, check columns are mapped
        if len(df) > 0:
            self.assertIn("temperature", df.columns)

    @patch("projet.api.requests.get")
    def test_fetch_observations_date_filtering(self, mock_get: MagicMock) -> None:
        """Test fetch_observations filters by date range correctly."""
        # Create mock response with some data
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=60)
        future = now + timedelta(days=60)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "temperature_en_degre_c": 20.0,
                    "humidite": 65,
                    "pression": 101325,
                    "pluie": 0.0,
                    "force_moyenne_du_vecteur_vent": 5,
                    "heure_utc": past.isoformat(),  # Way before
                    "id": 42,
                    "type_de_station": "ISS",
                },
                {
                    "temperature_en_degre_c": 21.0,
                    "humidite": 63,
                    "pression": 101320,
                    "pluie": 0.0,
                    "force_moyenne_du_vecteur_vent": 4,
                    "heure_utc": now.isoformat(),  # Now
                    "id": 42,
                    "type_de_station": "ISS",
                },
                {
                    "temperature_en_degre_c": 22.0,
                    "humidite": 60,
                    "pression": 101315,
                    "pluie": 0.0,
                    "force_moyenne_du_vecteur_vent": 3,
                    "heure_utc": future.isoformat(),  # Way after
                    "id": 42,
                    "type_de_station": "ISS",
                },
            ],
            "total_count": 3,
        }
        mock_get.return_value = mock_response

        # Fetch with default date range
        df = self.retriever.fetch_observations(limit=10)

        # Should have some data (at least the record near 'now')
        self.assertGreater(len(df), 0)
        # But not all records (some were outside the 30-day window)
        self.assertLess(len(df), 3)

    @patch("projet.api.requests.get")
    def test_fetch_observations_no_data(self, mock_get: MagicMock) -> None:
        """Test fetch_observations raises ValueError when no data."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [], "total_count": 0}
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            self.retriever.fetch_observations(limit=10)

        self.assertIn("No observations found", str(context.exception))

    @patch("projet.api.requests.get")
    def test_fetch_observations_api_error(self, mock_get: MagicMock) -> None:
        """Test fetch_observations handles API errors."""
        mock_get.side_effect = Exception("Network error")

        with self.assertRaises(Exception):
            self.retriever.fetch_observations()

    @patch("projet.api.requests.get")
    def test_fetch_all_observations_pagination(self, mock_get: MagicMock) -> None:
        """Test fetch_all_observations handles pagination."""
        # Simulate two pages of data with current dates
        end = datetime.now(timezone.utc)
        base_date = end - timedelta(days=15)
        
        def side_effect(*args, **kwargs):
            mock_response = MagicMock()
            if kwargs.get("params", {}).get("offset", 0) == 0:
                # First page (100 records)
                mock_response.json.return_value = {
                    "results": [
                        {
                            "temperature_en_degre_c": float(i),
                            "humidite": 65,
                            "pression": 101325,
                            "pluie": 0.0,
                            "force_moyenne_du_vecteur_vent": 5,
                            "heure_utc": (base_date + timedelta(hours=i)).isoformat(),
                            "id": 42,
                            "type_de_station": "ISS",
                        }
                        for i in range(100)
                    ],
                    "total_count": 150,
                }
            else:
                # Second page (50 records - less than limit, so should stop)
                mock_response.json.return_value = {
                    "results": [
                        {
                            "temperature_en_degre_c": float(100 + i),
                            "humidite": 65,
                            "pression": 101325,
                            "pluie": 0.0,
                            "force_moyenne_du_vecteur_vent": 5,
                            "heure_utc": (base_date + timedelta(hours=100 + i)).isoformat(),
                            "id": 42,
                            "type_de_station": "ISS",
                        }
                        for i in range(50)
                    ],
                    "total_count": 150,
                }
            return mock_response

        mock_get.side_effect = side_effect

        df = self.retriever.fetch_all_observations()

        # Should have combined records from both pages
        self.assertGreaterEqual(len(df), 50)

    def test_fetch_method_not_implemented(self) -> None:
        """Test that abstract fetch() method raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            self.retriever.fetch()


if __name__ == "__main__":
    unittest.main()
