# Linked List Implementation for Weather Station Display

## Overview

This module implements a **singly linked list** data structure optimized for sequential display and management of weather station data. It provides both a generic linked list and a specialized weather station linked list with meteorological features.

## Features

### 1. Generic LinkedList Class

A type-safe, generic linked list supporting all standard operations:

- **Append/Prepend**: Add elements to the end or beginning
- **Insert at Index**: Insert at any position
- **Remove**: Remove by value or by index
- **Search**: Find elements by value or check membership
- **Access**: Get element at specific index
- **Iteration**: Iterate through all elements
- **Length**: Track list size efficiently

#### Usage Example

```python
from projet.linked_list import LinkedList

ll = LinkedList()
ll.append(10)
ll.append(20)
ll.append(30)

print(list(ll))  # [10, 20, 30]
print(ll.find(20))  # 1
ll.remove(20)
print(list(ll))  # [10, 30]
```

### 2. WeatherStationNode Class

A node that stores weather station data with metadata:

**Attributes:**
- `station_id`: Unique identifier (string)
- `station_name`: Display name
- `data`: pandas DataFrame with observations

**Methods:**
- `display_summary()`: Format and return station summary with statistics
- `__eq__`: Compare nodes by station_id

#### Usage Example

```python
import pandas as pd
from projet.linked_list import WeatherStationNode

dates = pd.date_range('2024-01-01', periods=5, tz='UTC')
df = pd.DataFrame({
    'temperature': [20, 21, 22, 23, 24],
    'humidity': [60, 62, 64, 66, 68]
}, index=dates)

node = WeatherStationNode('paris_1', 'Paris Station', df)
print(node.display_summary())
```

### 3. WeatherStationLinkedList Class

A specialized linked list for managing multiple weather stations with meteorological operations:

**Key Methods:**

- `add_station(id, name, dataframe)` - Add a weather station
- `remove_station(id)` - Remove a station by ID
- `get_station(id)` - Retrieve station by ID
- `get_station_by_index(index)` - Access station by position
- `list_stations()` - Get all station descriptions
- `display_all(verbose=True)` - Display all stations with optional statistics
- `display_station(id)` - Show specific station details
- `get_combined_dataframe()` - Merge all station data with metadata
- `filter_by_date(start, end)` - Create filtered list for date range
- `__len__()` - Get number of stations
- `__iter__()` - Iterate through stations

#### Usage Example

```python
from projet.linked_list import WeatherStationLinkedList
import pandas as pd

# Create list
stations = WeatherStationLinkedList()

# Add stations
df1 = pd.DataFrame({'temp': [20, 21, 22]})
df2 = pd.DataFrame({'temp': [15, 16, 17]})

stations.add_station('paris', 'Paris', df1)
stations.add_station('lyon', 'Lyon', df2)

# Display all
stations.display_all(verbose=False)

# Get combined data
combined = stations.get_combined_dataframe()
print(combined)
```

## Architecture

```
LinkedList[T]
├── Node[T] (each node stores data + next pointer)
└── Methods: append, insert, remove, find, iterate

WeatherStationNode
├── station_id: str
├── station_name: str
├── data: DataFrame
└── Methods: display_summary(), __eq__()

WeatherStationLinkedList
├── stations: LinkedList[WeatherStationNode]
└── Methods: add/remove/get stations, filter, combine
```

## Key Design Decisions

### 1. **Generic with TypeVar**
```python
T = TypeVar('T')
class LinkedList(Generic[T]):
    # Works with any data type
```
Allows the base LinkedList to work with any data type, including custom WeatherStationNode.

### 2. **Node Equality by Station ID**
```python
def __eq__(self, other) -> bool:
    return self.station_id == other.station_id
```
Enables `remove()` to work with station lookups without modifying data.

### 3. **Timezone-Aware Date Filtering**
```python
start_ts = pd.Timestamp(start_date, tz='UTC')
mask = station.data.index >= start_ts
```
Prevents pandas comparison errors with timezone-aware indexes.

### 4. **Non-Destructive Filtering**
```python
filtered = original_list.filter_by_date(start, end)
# original_list unchanged, filtered is new list
```
Returns new list instead of modifying original (functional programming style).

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| append | O(n) | Must traverse to end |
| prepend | O(1) | Direct head insertion |
| insert_at | O(n) | Traverse to position |
| remove | O(n) | Search required |
| get_at | O(n) | Sequential access |
| find | O(n) | Sequential search |
| iterate | O(n) | Visit all nodes |
| length | O(1) | Cached value |

## Comparison with Alternatives

### vs. Python List
- **Linked List**: O(1) prepend, sequential memory
- **Python List**: O(n) prepend, contiguous memory, random access

### vs. Deque
- **Linked List**: No size overhead, simpler
- **Deque**: O(1) both ends, but larger memory footprint

For weather station display (sequential, append-only), linked list is suitable.

## Testing

Comprehensive test suite with 45 tests:

```bash
# Run linked list tests
pytest tests/test_linked_list.py -v

# Test coverage includes:
# - Generic LinkedList: 23 tests
# - WeatherStationNode: 6 tests
# - WeatherStationLinkedList: 16 tests
```

**Test Categories:**
- Empty list operations
- Insertion (beginning, middle, end)
- Removal (by value, by index)
- Search and containment
- Iteration and string representation
- Station management
- Date filtering with timezone awareness
- DataFrame combining

## CLI Integration

Display stations using the linked list via CLI:

```bash
# Display Toulouse stations
python -m projet stations --source toulouse

# Display multiple Meteostat stations
python -m projet stations --source meteo

# Show detailed statistics
python -m projet stations --source toulouse --verbose

# Filter by date range
python -m projet stations --source toulouse --start 2024-11-01 --end 2024-11-30
```

## Examples

See `linked_list_examples.py` for complete working examples:

```python
python linked_list_examples.py
```

Examples demonstrate:
1. Generic linked list operations
2. Creating weather station lists
3. Iterating sequentially through stations
4. Filtering and combining data
5. Removing stations

## Data Flow

```
CSV/API Data
    ↓
DataFrame (indexed by timestamp, tz-aware)
    ↓
WeatherStationNode (wraps DataFrame with metadata)
    ↓
LinkedList[WeatherStationNode] (sequential structure)
    ↓
WeatherStationLinkedList (specialized interface)
    ↓
Display/Filter/Combine operations
```

## Advantages of Linked List for Weather Data

1. **Sequential Display**: Natural iteration matches user expectations
2. **Variable Size**: Easy to add/remove stations dynamically
3. **Efficient Prepend**: Add newly-fetched stations to front
4. **Memory Efficient**: No wasted capacity like dynamic arrays
5. **No Random Access Overhead**: Meteorological apps don't need O(1) indexing

## Best Practices

### Adding Stations

```python
# Good: Add with clean data
df = retriever.fetch_observations(...)
stations.add_station(id, name, df)

# Avoid: Adding with raw/uncleaned data
stations.add_station(id, name, raw_df)
```

### Filtering

```python
# Good: Create new list, preserve original
filtered = stations.filter_by_date('2024-01-01', '2024-12-31')

# Less efficient: Manually iterate and rebuild
```

### Combining Data

```python
# Good: Use built-in method
combined = stations.get_combined_dataframe()

# Avoid: Manual concatenation in loop
```

## Future Enhancements

1. **Doubly Linked List**: Add backward iteration
2. **Circular List**: Connect tail to head
3. **Sorted Insertion**: Auto-sort by station name/date
4. **Caching**: Cache combined DataFrame
5. **Parallel Processing**: Concurrent station operations

## References

- Data Structures: Linked Lists (classic CS concept)
- Python Type Hints: PEP 484, typing module
- Pandas: DataFrame timezone-aware operations
- Pytest: Unit testing framework
