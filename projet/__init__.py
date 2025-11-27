"""Station Meteo: Weather data retrieval, cleaning, and analysis package."""

from projet.api import ToulouseMeteoAPIRetriever, MeteostatDataRetriever
from projet.cleaner import DataCleaner
from projet.retriever import CSVDataRetriever, DataRetriever

__all__ = [
    "DataRetriever",
    "CSVDataRetriever",
    "ToulouseMeteoAPIRetriever",
    "MeteostatDataRetriever",
    "DataCleaner",
]
__version__ = "0.1.0"
