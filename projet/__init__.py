"""Station Meteo: Weather data retrieval, cleaning, and analysis package."""

from projet.api import ToulouseMeteoAPIRetriever, MeteostatDataRetriever
from projet.cleaner import DataCleaner
from projet.retriever import CSVDataRetriever, DataRetriever
from projet.linked_list import LinkedList, WeatherStationLinkedList, WeatherStationNode
from projet.queue import (Queue, PriorityQueue, ExtractionQueue, ExtractionTask,TaskStatus, TaskPriority)
from projet.config import (ConfigDict, StationsDict, ConfigurationManager,StationConfig, APIConfig, ExtractionConfig, OutputConfig,ConfigKey, DataSource, OutputFormat)

__all__ = [
    "DataRetriever",
    "CSVDataRetriever",
    "ToulouseMeteoAPIRetriever",
    "MeteostatDataRetriever",
    "DataCleaner",
    "LinkedList",
    "WeatherStationLinkedList",
    "WeatherStationNode",
    "Queue",
    "PriorityQueue",
    "ExtractionQueue",
    "ExtractionTask",
    "TaskStatus",
    "TaskPriority",
    "ConfigDict",
    "StationsDict",
    "ConfigurationManager",
    "StationConfig",
    "APIConfig",
    "ExtractionConfig",
    "OutputConfig",
    "ConfigKey",
    "DataSource",
    "OutputFormat",
]
__version__ = "0.1.0"
