"""Command-line interface for the weather app."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import List, Optional

from projet.retriever import CSVDataRetriever
from projet.cleaner import DataCleaner
from projet.api import MeteostatDataRetriever, ToulouseMeteoAPIRetriever
from projet.linked_list import WeatherStationLinkedList

logger = logging.getLogger(__name__)


class WeatherApp:
    """Encapsulates CLI and app-level orchestration."""

    def __init__(
        self,
        retriever: CSVDataRetriever | None = None,
        default_csv_name: str = "42-station-meteo-toulouse-parc-compans-cafarelli.csv",
    ) -> None:
        self.retriever = retriever or CSVDataRetriever()
        self.default_csv_name = default_csv_name

    def _create_arg_parser(self) -> argparse.ArgumentParser:
        """Create and configure CLI argument parser.

        Returns:
            Configured ArgumentParser instance.
        """
        parser = argparse.ArgumentParser(
            description="Weather data retrieval and analysis tool"
        )

        subparsers = parser.add_subparsers(
            dest="command", help="Available commands"
        )

        # CSV command
        csv_parser = subparsers.add_parser(
            "csv", help="Load weather data from CSV file"
        )
        csv_parser.add_argument(
            "csv",
            nargs="?",
            help="Path to CSV file (default: bundled filename)",
        )
        csv_parser.add_argument(
            "--tz",
            default="UTC",
            help="Target timezone for timestamps (default: UTC)",
        )
        csv_parser.add_argument(
            "--sample",
            type=int,
            default=5,
            help="Number of rows to show in sample",
        )

        # Toulouse API command
        toulouse_parser = subparsers.add_parser(
            "toulouse", help="Fetch data from Toulouse Métropole API"
        )
        toulouse_parser.add_argument(
            "--start",
            help="Start date (YYYY-MM-DD, default: 30 days ago)",
        )
        toulouse_parser.add_argument(
            "--end",
            help="End date (YYYY-MM-DD, default: today)",
        )
        toulouse_parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Maximum records to fetch (default: 100, max: 10000)",
        )
        toulouse_parser.add_argument(
            "--sample",
            type=int,
            default=5,
            help="Number of rows to show",
        )

        # Meteostat command
        meteo_parser = subparsers.add_parser(
            "meteo", help="Fetch data from Meteostat API"
        )
        meteo_subparsers = meteo_parser.add_subparsers(
            dest="meteo_command", help="Meteostat operations"
        )

        # Meteostat station command
        station_parser = meteo_subparsers.add_parser(
            "station", help="Get data for specific station"
        )
        station_parser.add_argument(
            "station_id",
            help="Meteostat station ID (e.g., '10438' for Paris Orly)",
        )
        station_parser.add_argument(
            "--start",
            help="Start date (YYYY-MM-DD, default: 1 year ago)",
        )
        station_parser.add_argument(
            "--end",
            help="End date (YYYY-MM-DD, default: today)",
        )
        station_parser.add_argument(
            "--sample",
            type=int,
            default=5,
            help="Number of rows to show",
        )

        # Meteostat coordinates command
        coords_parser = meteo_subparsers.add_parser(
            "coords", help="Get data for nearest station to coordinates"
        )
        coords_parser.add_argument(
            "latitude", type=float, help="Latitude"
        )
        coords_parser.add_argument(
            "longitude", type=float, help="Longitude"
        )
        coords_parser.add_argument(
            "--start",
            help="Start date (YYYY-MM-DD)",
        )
        coords_parser.add_argument(
            "--end",
            help="End date (YYYY-MM-DD)",
        )
        coords_parser.add_argument(
            "--radius",
            type=float,
            default=25.0,
            help="Search radius in km (default: 25)",
        )
        coords_parser.add_argument(
            "--sample",
            type=int,
            default=5,
            help="Number of rows to show",
        )

        # Meteostat search command
        search_parser = meteo_subparsers.add_parser(
            "search", help="Search for stations"
        )
        search_parser.add_argument(
            "--query",
            help="Station name search query",
        )
        search_parser.add_argument(
            "--country",
            help="ISO 3166-1 alpha-2 country code (e.g., 'FR')",
        )

        # Linked list stations command
        stations_parser = subparsers.add_parser(
            "stations", help="Display all stations in a linked list"
        )
        stations_parser.add_argument(
            "--source",
            choices=["toulouse", "meteo"],
            default="toulouse",
            help="Data source to fetch from (default: toulouse)",
        )
        stations_parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed statistics for each station",
        )
        stations_parser.add_argument(
            "--start",
            help="Start date (YYYY-MM-DD, default: 30 days ago)",
        )
        stations_parser.add_argument(
            "--end",
            help="End date (YYYY-MM-DD, default: today)",
        )
        stations_parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Maximum records per station (default: 100)",
        )

        return parser

    def run(self, argv: Optional[List[str]] = None) -> int:
        """Run the app with given CLI arguments.

        Args:
            argv: Command-line arguments (if None, uses sys.argv).

        Returns:
            Exit code (0 on success, 2 on error).
        """
        parser = self._create_arg_parser()
        args = parser.parse_args(argv)

        if not args.command:
            parser.print_help()
            return 0

        try:
            if args.command == "csv":
                return self._handle_csv(args)
            elif args.command == "toulouse":
                return self._handle_toulouse(args)
            elif args.command == "meteo":
                if not args.meteo_command:
                    parser.parse_args([args.command, "--help"])
                    return 0
                if args.meteo_command == "station":
                    return self._handle_meteo_station(args)
                elif args.meteo_command == "coords":
                    return self._handle_meteo_coords(args)
                elif args.meteo_command == "search":
                    return self._handle_meteo_search(args)
            elif args.command == "stations":
                return self._handle_stations(args)
        except Exception as exc:
            logger.error("Error: %s", exc)
            return 2

        return 0

    def _handle_csv(self, args) -> int:
        """Handle CSV command."""
        if args.csv:
            csv_path = Path(args.csv)
        else:
            csv_path = Path(__file__).parent.parent / self.default_csv_name

        retriever = CSVDataRetriever(DataCleaner(tz=args.tz))

        try:
            df = retriever.fetch(csv_path)
        except Exception as exc:
            logger.error("Failed to fetch CSV: %s", exc)
            return 2

        print("\n=== CSV Data Sample ===")
        print(df.head(args.sample).to_string())
        print("\nColumns:", list(df.columns))
        print("\nDescriptive stats:")
        print(df.describe())
        return 0

    def _handle_toulouse(self, args) -> int:
        """Handle Toulouse Métropole API command."""
        retriever = ToulouseMeteoAPIRetriever()

        try:
            # Get total count first
            total = retriever.get_total_count(args.start, args.end)
            logger.info("Total observations available: %d", total)

            df = retriever.fetch_observations(
                start_date=args.start,
                end_date=args.end,
                limit=args.limit,
            )
        except Exception as exc:
            logger.error("Failed to fetch Toulouse data: %s", exc)
            return 2

        print(f"\n=== Toulouse Métropole Weather Data ===")
        print(f"Period: {args.start or '30 days ago'} to {args.end or 'today'}")
        print(f"Records retrieved: {len(df)} (total available: {total})")
        print(f"\n{df.head(args.sample).to_string()}")
        print(f"\nColumns: {list(df.columns)}")
        print("\nDescriptive stats:")
        print(df.describe())
        return 0

    def _handle_meteo_station(self, args) -> int:
        """Handle Meteostat station command."""
        retriever = MeteostatDataRetriever()

        try:
            df = retriever.fetch_by_station(
                args.station_id,
                start_date=args.start,
                end_date=args.end,
            )
        except Exception as exc:
            logger.error("Failed to fetch Meteostat data: %s", exc)
            return 2

        print(f"\n=== Meteostat Data for Station {args.station_id} ===")
        print(df.head(args.sample).to_string())
        print(f"\nRows retrieved: {len(df)}")
        print("Columns:", list(df.columns))
        print("\nDescriptive stats:")
        print(df.describe())
        return 0

    def _handle_meteo_coords(self, args) -> int:
        """Handle Meteostat coordinates command."""
        retriever = MeteostatDataRetriever()

        try:
            df = retriever.fetch_by_coordinates(
                latitude=args.latitude,
                longitude=args.longitude,
                start_date=args.start,
                end_date=args.end,
                radius_km=args.radius,
            )
        except Exception as exc:
            logger.error("Failed to fetch Meteostat data: %s", exc)
            return 2

        print(f"\n=== Meteostat Data for ({args.latitude}, {args.longitude}) ===")
        print(df.head(args.sample).to_string())
        print(f"\nRows retrieved: {len(df)}")
        print("Columns:", list(df.columns))
        return 0

    def _handle_meteo_search(self, args) -> int:
        """Handle Meteostat search command."""
        retriever = MeteostatDataRetriever()

        try:
            results = retriever.search_stations(
                query=args.query,
                country=args.country,
            )
        except Exception as exc:
            logger.error("Failed to search stations: %s", exc)
            return 2

        if results.empty:
            print("No stations found.")
            return 0

        print("\n=== Stations Found ===")
        print(results.to_string())
        print(f"\nTotal: {len(results)} stations")
        return 0

    def _handle_stations(self, args) -> int:
        """Handle stations linked list display command."""
        stations_ll = WeatherStationLinkedList()

        try:
            if args.source == "toulouse":
                # Fetch from Toulouse API - single station
                retriever = ToulouseMeteoAPIRetriever()
                df = retriever.fetch_observations(
                    start_date=args.start,
                    end_date=args.end,
                    limit=args.limit,
                )
                stations_ll.add_station(
                    "toulouse-parc-compans",
                    "Toulouse - Parc Compans Cafarelli",
                    df
                )
            else:
                # Fetch from Meteostat - can be multiple stations
                # For demo, fetch from a few French stations
                retriever = MeteostatDataRetriever()
                station_ids = ["10438", "10383"]  # Paris Orly and Le Bourget
                
                for station_id in station_ids:
                    try:
                        df = retriever.fetch_by_station(
                            station_id,
                            start_date=args.start,
                            end_date=args.end,
                        )
                        station_info = retriever._get_station(station_id)
                        station_name = station_info.name if station_info is not None else f"Station {station_id}"
                        stations_ll.add_station(station_id, station_name, df)
                    except Exception as e:
                        logger.warning("Failed to fetch station %s: %s", station_id, e)
                        continue

        except Exception as exc:
            logger.error("Failed to fetch stations: %s", exc)
            return 2

        if len(stations_ll) == 0:
            print("No stations loaded.")
            return 2

        # Display all stations from linked list
        stations_ll.display_all(verbose=args.verbose)
        
        # Show station list summary
        print(f"\n{'='*60}")
        print("LINKED LIST SUMMARY")
        print(f"{'='*60}")
        print(f"Total stations in list: {len(stations_ll)}\n")
        for i, station in enumerate(stations_ll.list_stations(), 1):
            print(f"{i}. {station}")

        return 0
