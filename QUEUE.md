# Queue Implementation for Weather Data Extraction

## Overview

A comprehensive **queue (FIFO)** implementation system for managing weather data extraction tasks. The module provides three main queue types designed to handle different extraction patterns and scenarios:

1. **Queue** - Simple FIFO (First-In-First-Out) queue
2. **PriorityQueue** - Priority-based queue for task prioritization  
3. **ExtractionQueue** - Specialized queue for weather data extraction with retry logic and status tracking

## Key Features

### 📦 Core Queue (`Queue[T]`)

- **FIFO Operations**: Standard enqueue, dequeue, peek operations
- **Generic Type Safety**: Full type hints with `TypeVar[T]`
- **Thread-Safe Support**: Optional thread-safe operations with locks
- **Size Management**: Optional max queue size enforcement
- **Full Iteration**: Iterate through all items without removal

#### Operations

```python
from projet.queue import Queue

queue = Queue(max_size=100, thread_safe=True)

# Enqueue items (O(1))
queue.enqueue("item1")
queue.enqueue("item2")

# Dequeue items (O(1))
item = queue.dequeue()

# Peek without removing (O(1))
next_item = queue.peek()

# Check status
size = queue.size()
is_empty = queue.is_empty()
is_full = queue.is_full()
```

### ⭐ Priority Queue (`PriorityQueue[T]`)

- **Priority-Based Ordering**: Items processed by priority level
- **FIFO for Same Priority**: Items with same priority use FIFO order
- **Automatic Sorting**: Insertion maintains priority order
- **Thread-Safe Support**: Optional thread-safe operations

#### Operations

```python
from projet.queue import PriorityQueue, ExtractionTask, TaskPriority

pq = PriorityQueue(thread_safe=True)

# Create tasks with priorities
task_high = ExtractionTask(
    "task1", "station1", "Paris",
    "2024-01-01", "2024-12-31",
    priority=TaskPriority.HIGH
)
task_low = ExtractionTask(
    "task2", "station2", "Lyon",
    "2024-01-01", "2024-12-31",
    priority=TaskPriority.LOW
)

# Enqueue in any order
pq.enqueue(task_low)
pq.enqueue(task_high)

# Dequeue in priority order (HIGH first)
next_task = pq.dequeue()  # Gets task_high
```

#### Priority Levels

```python
class TaskPriority(Enum):
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0
```

### 🎯 Extraction Queue (`ExtractionQueue`)

Specialized queue for weather data extraction with advanced features:

#### Features

- **Task Management**: Add, track, and process extraction tasks
- **Priority Processing**: Tasks processed by priority level
- **Status Tracking**: PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED
- **Retry Mechanism**: Automatic retry with configurable max attempts
- **Result Storage**: Store and retrieve extraction results
- **Statistics**: Real-time queue statistics
- **Thread-Safe**: Fully thread-safe for concurrent processing

#### Task States

```
PENDING ─────────────┐
                     ├──→ PROCESSING ─┬──→ COMPLETED
                     │                │
         CANCELLED ←─┘    ERROR ──────┼──→ RETRY (back to PENDING)
                                      │
                                      └──→ FAILED
```

#### Basic Usage

```python
from projet.queue import ExtractionQueue, ExtractionTask
import pandas as pd

# Create extraction queue
eq = ExtractionQueue(thread_safe=True)

# Create and add task
task = ExtractionTask(
    task_id="task_paris",
    station_id="paris_1",
    station_name="Paris Center",
    start_date="2024-01-01",
    end_date="2024-12-31",
    source="toulouse",
    priority=TaskPriority.HIGH
)
eq.add_task(task)

# Process tasks
while eq.get_pending_count() > 0:
    # Get next task
    task = eq.get_next_task()
    
    # Process extraction (your code here)
    try:
        df = extract_weather_data(task.station_id, task.start_date, task.end_date)
        # Mark complete
        eq.complete_task(task.task_id, df)
    except Exception as e:
        # Mark failed with retry
        eq.fail_task(task.task_id, str(e), retry=True)

# Check results
stats = eq.get_stats()
print(f"Completed: {stats['completed']}, Failed: {stats['failed']}")
```

#### Advanced Features

##### Task Metadata

```python
task = ExtractionTask(
    "task1", "station1", "Paris", "2024-01-01", "2024-01-31",
    metadata={
        'priority_reason': 'High demand location',
        'data_quality': 'strict',
        'required_fields': ['temperature', 'humidity', 'pressure']
    }
)
```

##### Status Monitoring

```python
# Get individual task status
status = eq.get_task_status("task_id")

# Get all tasks organized by status
all_tasks = eq.get_all_tasks()
for task in all_tasks['completed']:
    print(f"✓ {task.station_name}: {len(eq.get_task_result(task.task_id))} records")

for task in all_tasks['failed']:
    print(f"✗ {task.station_name}: {task.error_message}")
```

##### Retry Configuration

```python
task = ExtractionTask(
    "task1", "station1", "Paris", "2024-01-01", "2024-12-31",
    max_retries=3  # Allow up to 3 retry attempts
)

# Retries are automatic when fail_task called with retry=True
eq.fail_task(task.task_id, "Connection timeout", retry=True)
# Task goes back to PENDING if retry_count < max_retries
```

## Class Reference

### ExtractionTask

Represents a weather data extraction task.

```python
@dataclass
class ExtractionTask:
    task_id: str                           # Unique task identifier
    station_id: str                        # Weather station ID
    station_name: str                      # Station display name
    start_date: str                        # Date range start (YYYY-MM-DD)
    end_date: str                          # Date range end (YYYY-MM-DD)
    source: str = "toulouse"               # Data source
    priority: TaskPriority = NORMAL        # Task priority
    created_at: datetime = utcnow()        # Creation timestamp
    status: TaskStatus = PENDING           # Current status
    result: Optional[DataFrame] = None     # Extraction result
    error_message: Optional[str] = None    # Error description
    retry_count: int = 0                   # Current retry count
    max_retries: int = 3                   # Maximum retries allowed
    metadata: dict = {}                    # Additional metadata
```

### ExtractionQueue Methods

#### Task Management

```python
# Add task to queue
eq.add_task(task: ExtractionTask) -> bool

# Get next task from queue
eq.get_next_task() -> Optional[ExtractionTask]

# Mark task as completed
eq.complete_task(task_id: str, result: DataFrame) -> bool

# Mark task as failed (with optional retry)
eq.fail_task(task_id: str, error_message: str, retry: bool = True) -> bool

# Get task status
eq.get_task_status(task_id: str) -> Optional[TaskStatus]

# Get task result
eq.get_task_result(task_id: str) -> Optional[DataFrame]
```

#### Statistics

```python
# Get count of pending tasks
eq.get_pending_count() -> int

# Get count of processing tasks
eq.get_processing_count() -> int

# Get count of completed tasks
eq.get_completed_count() -> int

# Get count of failed tasks
eq.get_failed_count() -> int

# Get all statistics
eq.get_stats() -> dict

# Get all tasks organized by status
eq.get_all_tasks() -> dict[str, list[ExtractionTask]]
```

## Performance Characteristics

| Operation | Time Complexity | Space | Notes |
|-----------|------------------|-------|-------|
| Enqueue (Queue) | O(1) | O(1) | Append to deque |
| Dequeue (Queue) | O(1) | O(1) | Pop from left |
| Enqueue (PriorityQueue) | O(n) | O(1) | Linear search for position |
| Dequeue (PriorityQueue) | O(1) | O(1) | Remove from head |
| Complete Task | O(1) | O(1) | Dictionary insertion |
| Fail Task | O(n) | O(1) | Re-enqueue if retry |
| Get Stats | O(1) | O(1) | Pre-calculated counts |

## Thread Safety

All queue implementations support optional thread-safe operations using `threading.Lock()`:

```python
# Thread-safe queue
queue = Queue(thread_safe=True)
pq = PriorityQueue(thread_safe=True)
eq = ExtractionQueue(thread_safe=True)  # Default is True

# Concurrent access example
from threading import Thread

def producer(eq, count):
    for i in range(count):
        task = ExtractionTask(f"task_{i}", f"s{i}", f"City {i}", 
                             "2024-01-01", "2024-12-31")
        eq.add_task(task)

def consumer(eq, count):
    for _ in range(count):
        task = eq.get_next_task()
        if task:
            eq.complete_task(task.task_id, pd.DataFrame())

t1 = Thread(target=producer, args=(eq, 50))
t2 = Thread(target=consumer, args=(eq, 50))

t1.start()
t2.start()
t1.join()
t2.join()
```

## Examples

### Example 1: Basic FIFO Processing

```python
queue = Queue()
for i in range(10):
    queue.enqueue(i)

while not queue.is_empty():
    item = queue.dequeue()
    print(f"Processing: {item}")
```

### Example 2: Priority Task Processing

```python
eq = ExtractionQueue()

# Add mixed priority tasks
for i in range(5):
    task = ExtractionTask(
        f"task_{i}", f"station_{i}", f"City {i}",
        "2024-01-01", "2024-12-31",
        priority=TaskPriority.NORMAL if i % 2 else TaskPriority.HIGH
    )
    eq.add_task(task)

# Process in priority order
while eq.get_pending_count() > 0:
    task = eq.get_next_task()
    # High priority tasks processed first
```

### Example 3: Failure Handling with Retries

```python
eq = ExtractionQueue()
task = ExtractionTask("task1", "s1", "Paris", "2024-01-01", "2024-12-31")
eq.add_task(task)

for attempt in range(1, 4):
    task = eq.get_next_task()
    try:
        result = extract_data(task.station_id)
        eq.complete_task(task.task_id, result)
        break
    except Exception as e:
        will_retry = eq.fail_task(task.task_id, str(e), retry=True)
        if not will_retry:
            print(f"Task permanently failed after {attempt} attempts")
```

### Example 4: Batch Processing

```python
eq = ExtractionQueue()

# Add all tasks
for config in station_configs:
    task = ExtractionTask(**config)
    eq.add_task(task)

# Process batch
results = {}
while eq.get_pending_count() > 0:
    task = eq.get_next_task()
    try:
        df = fetch_weather_data(task.station_id, task.start_date, task.end_date)
        eq.complete_task(task.task_id, df)
        results[task.station_id] = df
    except Exception as e:
        eq.fail_task(task.task_id, str(e), retry=True)

# Summary
stats = eq.get_stats()
print(f"Successfully extracted: {stats['completed']} stations")
print(f"Failed: {stats['failed']} stations")
```

## Integration with Existing Code

The queue module integrates seamlessly with existing weather data retrieval:

```python
from projet import DataRetriever, ExtractionQueue, ExtractionTask

# Set up retriever
retriever = ToulouseMeteoAPIRetriever()

# Create extraction queue
eq = ExtractionQueue()

# Add extraction tasks from configuration
for station in stations_config:
    task = ExtractionTask(
        task_id=f"extract_{station['id']}",
        station_id=station['id'],
        station_name=station['name'],
        start_date="2024-01-01",
        end_date="2024-12-31",
        source="toulouse",
        priority=TaskPriority.HIGH if station.get('priority') else TaskPriority.NORMAL
    )
    eq.add_task(task)

# Process all tasks
while eq.get_pending_count() > 0:
    task = eq.get_next_task()
    try:
        df = retriever.retrieve(
            station_id=task.station_id,
            start_date=task.start_date,
            end_date=task.end_date
        )
        eq.complete_task(task.task_id, df)
    except Exception as e:
        eq.fail_task(task.task_id, str(e), retry=True)

# Generate report
stats = eq.get_stats()
all_tasks = eq.get_all_tasks()

print(f"Extraction Summary:")
print(f"  Completed: {stats['completed']}")
print(f"  Failed: {stats['failed']}")
print(f"  Total: {stats['total']}")
```

## Best Practices

### 1. Task Priority Assignment

```python
# Use appropriate priority levels
critical_stations = ["Paris", "Lyon", "Marseille"]  # HIGH/URGENT
normal_stations = ["Other cities"]  # NORMAL
archive_stations = ["Historical data"]  # LOW

for station in critical_stations:
    task = ExtractionTask(..., priority=TaskPriority.HIGH)
```

### 2. Error Handling

```python
# Distinguish between retryable and permanent errors
try:
    data = extract(task)
except ConnectionError as e:
    # Retryable
    eq.fail_task(task.task_id, str(e), retry=True)
except ValueError as e:
    # Permanent
    eq.fail_task(task.task_id, str(e), retry=False)
```

### 3. Progress Monitoring

```python
# Track progress in long-running extractions
total_tasks = eq.get_stats()['total']
completed = 0

while eq.get_pending_count() > 0:
    task = eq.get_next_task()
    try:
        data = extract(task)
        eq.complete_task(task.task_id, data)
        completed += 1
        progress = (completed / total_tasks) * 100
        print(f"Progress: {progress:.1f}%")
    except Exception as e:
        eq.fail_task(task.task_id, str(e), retry=True)
```

### 4. Resource Management

```python
# Limit queue size for memory management
eq = ExtractionQueue()  # Unlimited pending
# Add items as they're processed

# Or use fixed max_size for memory control
queue = Queue(max_size=1000)
```

## Testing

See `tests/test_queue.py` for comprehensive test suite covering:

- ✅ FIFO operations
- ✅ Priority ordering
- ✅ Task lifecycle
- ✅ Retry mechanism
- ✅ Thread safety
- ✅ Status tracking
- ✅ Statistics reporting

Run tests:

```bash
python -m pytest tests/test_queue.py -v
```

## Files

- `projet/queue.py` - Queue implementation (634 lines)
- `tests/test_queue.py` - Test suite (36 tests)
- `queue_examples.py` - 5 complete usage examples
