"""Entry point for running the package as a module."""

import logging
import sys

from projet.cli import WeatherApp

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

if __name__ == "__main__":
    app = WeatherApp()
    sys.exit(app.run())
