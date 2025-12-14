"""Linked list implementation for sequential weather station data display."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Iterator, Generic, TypeVar

import pandas as pd

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class Node(Generic[T]):
    """A node in the linked list.

    Attributes:
        data: The data stored in this node
        next: Reference to the next node (None if end of list)
    """
    data: T
    next: Optional[Node[T]] = None

    def __repr__(self) -> str:
        """String representation of node."""
        return f"Node({self.data})"


class LinkedList(Generic[T]):
    """A simple singly linked list implementation.

    Provides methods for insertion, deletion, traversal, and search
    operations on a linked list data structure.

    Attributes:
        head: The first node in the list (None if empty)
        _length: Cached length of the list

    Example:
        >>> ll = LinkedList()
        >>> ll.append(10)
        >>> ll.append(20)
        >>> ll.append(30)
        >>> for value in ll:
        ...     print(value)
        10
        20
        30
    """

    def __init__(self) -> None:
        """Initialize an empty linked list."""
        self.head: Optional[Node[T]] = None
        self._length: int = 0

    def append(self, data: T) -> None:
        """Append an element to the end of the list.

        Args:
            data: Element to append
        """
        new_node = Node(data)
        
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        
        self._length += 1
        logger.debug("Appended element to linked list (length: %d)", self._length)

    def prepend(self, data: T) -> None:
        """Prepend an element to the beginning of the list.

        Args:
            data: Element to prepend
        """
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._length += 1
        logger.debug("Prepended element to linked list (length: %d)", self._length)

    def insert_at(self, index: int, data: T) -> None:
        """Insert an element at a specific index.

        Args:
            index: Position to insert at (0 = beginning)
            data: Element to insert

        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index > self._length:
            raise IndexError(f"Index {index} out of range (list length: {self._length})")
        
        if index == 0:
            self.prepend(data)
            return
        
        new_node = Node(data)
        current = self.head
        
        for _ in range(index - 1):
            if current is None:
                raise IndexError("List is shorter than expected")
            current = current.next
        
        new_node.next = current.next
        current.next = new_node
        self._length += 1

    def remove(self, data: T) -> bool:
        """Remove the first occurrence of an element.

        Args:
            data: Element to remove

        Returns:
            True if element was removed, False if not found
        """
        if not self.head:
            return False
        
        # Check if head needs to be removed
        if self.head.data == data:
            self.head = self.head.next
            self._length -= 1
            logger.debug("Removed element from list (length: %d)", self._length)
            return True
        
        # Search rest of list
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self._length -= 1
                logger.debug("Removed element from list (length: %d)", self._length)
                return True
            current = current.next
        
        return False

    def remove_at(self, index: int) -> Optional[T]:
        """Remove element at a specific index.

        Args:
            index: Position to remove from

        Returns:
            The removed element, or None if index out of range

        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= self._length:
            raise IndexError(f"Index {index} out of range (list length: {self._length})")
        
        if index == 0:
            if self.head is None:
                raise IndexError("Cannot remove from empty list")
            data = self.head.data
            self.head = self.head.next
            self._length -= 1
            return data
        
        current = self.head
        for _ in range(index - 1):
            if current is None or current.next is None:
                raise IndexError("List is shorter than expected")
            current = current.next
        
        if current.next is None:
            raise IndexError("Index out of range")
        
        data = current.next.data
        current.next = current.next.next
        self._length -= 1
        return data

    def get_at(self, index: int) -> Optional[T]:
        """Get element at a specific index.

        Args:
            index: Position to retrieve from

        Returns:
            Element at index, or None if index out of range
        """
        if index < 0 or index >= self._length:
            return None
        
        current = self.head
        for _ in range(index):
            if current is None:
                return None
            current = current.next
        
        return current.data if current else None

    def find(self, data: T) -> int:
        """Find the index of an element.

        Args:
            data: Element to search for

        Returns:
            Index of element, or -1 if not found
        """
        current = self.head
        index = 0
        
        while current:
            if current.data == data:
                return index
            current = current.next
            index += 1
        
        return -1

    def contains(self, data: T) -> bool:
        """Check if an element is in the list.

        Args:
            data: Element to search for

        Returns:
            True if element found, False otherwise
        """
        return self.find(data) != -1

    def clear(self) -> None:
        """Clear all elements from the list."""
        self.head = None
        self._length = 0
        logger.debug("Linked list cleared")

    def __len__(self) -> int:
        """Return the length of the list."""
        return self._length

    def __iter__(self) -> Iterator[T]:
        """Iterate over elements in the list."""
        current = self.head
        while current:
            yield current.data
            current = current.next

    def __repr__(self) -> str:
        """String representation of the list."""
        elements = list(self)
        return f"LinkedList({elements})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        if not self.head:
            return "LinkedList([])"
        
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        
        return " -> ".join(elements) + " -> None"


class WeatherStationNode:
    """A weather station data node for linked list storage.

    Attributes:
        station_id: Unique identifier for the station
        station_name: Name of the weather station
        data: DataFrame with weather observations
    """

    def __init__(
        self,
        station_id: str,
        station_name: str,
        data: pd.DataFrame
    ) -> None:
        self.station_id = station_id
        self.station_name = station_name
        self.data = data

    def __eq__(self, other) -> bool:
        """Check equality based on station ID."""
        if not isinstance(other, WeatherStationNode):
            return False
        return self.station_id == other.station_id

    def __repr__(self) -> str:
        """String representation."""
        return f"WeatherStationNode(id={self.station_id}, name={self.station_name}, records={len(self.data)})"

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.station_name} ({self.station_id}): {len(self.data)} observations"

    def display_summary(self) -> str:
        """Display a summary of the station's weather data.

        Returns:
            Formatted string with station summary
        """
        if self.data.empty:
            return f"Station: {self.station_name}\nNo data available\n"
        
        summary = f"\n{'='*60}\n"
        summary += f"Station: {self.station_name} (ID: {self.station_id})\n"
        summary += f"Records: {len(self.data)}\n"
        summary += f"Date Range: {self.data.index.min()} to {self.data.index.max()}\n"
        summary += f"{'-'*60}\n"
        summary += self.data.head(3).to_string()
        summary += f"\n{'-'*60}\n"
        summary += "Statistics:\n"
        summary += self.data.describe().to_string()
        summary += f"\n{'='*60}\n"
        
        return summary


class WeatherStationLinkedList:
    """Linked list of weather stations for sequential display.

    Provides methods to manage and display weather data for multiple
    stations in a linked list structure.

    Example:
        >>> stations_ll = WeatherStationLinkedList()
        >>> stations_ll.add_station(station_id, station_name, df1)
        >>> stations_ll.add_station(station_id2, station_name2, df2)
        >>> stations_ll.display_all()
    """

    def __init__(self) -> None:
        """Initialize an empty weather station linked list."""
        self.stations: LinkedList[WeatherStationNode] = LinkedList()

    def add_station(
        self,
        station_id: str,
        station_name: str,
        data: pd.DataFrame
    ) -> None:
        """Add a weather station to the linked list.

        Args:
            station_id: Unique identifier for the station
            station_name: Display name of the station
            data: DataFrame with weather observations
        """
        node = WeatherStationNode(station_id, station_name, data)
        self.stations.append(node)
        logger.info("Added station: %s (%s) with %d records", station_name, station_id, len(data))

    def remove_station(self, station_id: str) -> bool:
        """Remove a station from the linked list.

        Args:
            station_id: ID of the station to remove

        Returns:
            True if station was removed, False if not found
        """
        # Find the station node
        for station in self.stations:
            if station.station_id == station_id:
                return self.stations.remove(station)
        return False

    def get_station(self, station_id: str) -> Optional[WeatherStationNode]:
        """Get a station by its ID.

        Args:
            station_id: ID of the station to retrieve

        Returns:
            WeatherStationNode if found, None otherwise
        """
        for station in self.stations:
            if station.station_id == station_id:
                return station
        return None

    def get_station_by_index(self, index: int) -> Optional[WeatherStationNode]:
        """Get a station by its index in the list.

        Args:
            index: Position in the list

        Returns:
            WeatherStationNode if index is valid, None otherwise
        """
        return self.stations.get_at(index)

    def list_stations(self) -> list[str]:
        """Get a list of all station names and IDs.

        Returns:
            List of formatted station descriptions
        """
        return [str(station) for station in self.stations]

    def display_all(self, verbose: bool = True) -> None:
        """Display all stations in sequence.

        Args:
            verbose: If True, show detailed stats. If False, show summary only.
        """
        if len(self.stations) == 0:
            print("No stations in the list.")
            return
        
        print(f"\n{'='*60}")
        print(f"WEATHER STATIONS LIST ({len(self.stations)} total)")
        print(f"{'='*60}\n")
        
        for i, station in enumerate(self.stations, 1):
            if verbose:
                print(station.display_summary())
            else:
                print(f"{i}. {station}")
                if not station.data.empty:
                    print(f"   Date Range: {station.data.index.min()} to {station.data.index.max()}")
                    print(f"   Records: {len(station.data)}")
                print()

    def display_station(self, station_id: str) -> bool:
        """Display a specific station's data.

        Args:
            station_id: ID of the station to display

        Returns:
            True if station found and displayed, False otherwise
        """
        station = self.get_station(station_id)
        if station:
            print(station.display_summary())
            return True
        return False

    def get_combined_dataframe(self) -> pd.DataFrame:
        """Combine all station data into a single DataFrame.

        Returns:
            DataFrame with all observations from all stations
        """
        all_data = []
        for station in self.stations:
            df = station.data.copy()
            df['station_id'] = station.station_id
            df['station_name'] = station.station_name
            all_data.append(df)
        
        if not all_data:
            return pd.DataFrame()
        
        return pd.concat(all_data, ignore_index=False)

    def filter_by_date(self, start_date, end_date) -> 'WeatherStationLinkedList':
        """Create a new linked list with data filtered by date range.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            New WeatherStationLinkedList with filtered data
        """
        filtered_list = WeatherStationLinkedList()
        
        for station in self.stations:
            # Parse dates to timezone-aware timestamps
            start_ts = pd.Timestamp(start_date, tz='UTC')
            end_ts = pd.Timestamp(end_date, tz='UTC')
            
            # Filter the DataFrame by date range
            mask = (station.data.index >= start_ts) & \
                   (station.data.index <= end_ts)
            filtered_data = station.data[mask]
            
            if not filtered_data.empty:
                filtered_list.add_station(
                    station.station_id,
                    station.station_name,
                    filtered_data
                )
        
        return filtered_list

    def __len__(self) -> int:
        """Return the number of stations in the list."""
        return len(self.stations)

    def __iter__(self) -> Iterator[WeatherStationNode]:
        """Iterate over all stations in the list."""
        return iter(self.stations)

    def __repr__(self) -> str:
        """String representation."""
        return f"WeatherStationLinkedList({len(self.stations)} stations)"
