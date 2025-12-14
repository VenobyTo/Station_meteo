"""Queue (FIFO) implementation for weather data extraction tasks.

This module provides queue data structures for managing weather data
extraction tasks in a First-In-First-Out (FIFO) manner, allowing
batching and sequential processing of data retrieval operations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Generic, TypeVar, Iterator, List
import threading
from collections import deque

import pandas as pd

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TaskStatus(Enum):
    """Status of an extraction task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for extraction tasks."""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0


@dataclass
class ExtractionTask:
    """Represents a weather data extraction task.

    Attributes:
        task_id: Unique identifier for the task
        station_id: Weather station identifier
        station_name: Station display name
        start_date: Data retrieval start date
        end_date: Data retrieval end date
        source: Data source (toulouse, meteostat, etc)
        priority: Task priority (affects queue order)
        created_at: Task creation timestamp
        status: Current task status
        result: Task result (DataFrame or error message)
        retry_count: Number of retry attempts
        max_retries: Maximum retry attempts allowed
        metadata: Additional task metadata
    """

    task_id: str
    station_id: str
    station_name: str
    start_date: str
    end_date: str
    source: str = "toulouse"
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[pd.DataFrame] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: dict = field(default_factory=dict)

    def __lt__(self, other: ExtractionTask) -> bool:
        """Compare tasks by priority (for sorting in priority queue)."""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at

    def __repr__(self) -> str:
        """String representation of task."""
        return (
            f"ExtractionTask(id={self.task_id}, station={self.station_name}, "
            f"status={self.status.value}, priority={self.priority.name})"
        )

    def __str__(self) -> str:
        """Human-readable representation."""
        return (
            f"Task {self.task_id}: {self.station_name} "
            f"({self.status.value}, {self.priority.name})"
        )

    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            'task_id': self.task_id,
            'station_id': self.station_id,
            'station_name': self.station_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'source': self.source,
            'priority': self.priority.name,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'has_result': self.result is not None,
            'error_message': self.error_message,
        }


class Queue(Generic[T]):
    """A thread-safe FIFO queue (First-In-First-Out).

    Provides basic queue operations with optional thread safety
    for concurrent access.

    Attributes:
        items: Internal deque for storing items
        max_size: Maximum queue size (None = unlimited)
        thread_lock: Lock for thread-safe operations
    """

    def __init__(self, max_size: Optional[int] = None, thread_safe: bool = False) -> None:
        """Initialize a new queue.

        Args:
            max_size: Maximum number of items in queue (None = unlimited)
            thread_safe: Enable thread-safe operations with locks
        """
        self.items: deque[T] = deque()
        self.max_size = max_size
        self.thread_safe = thread_safe
        self._lock = threading.Lock() if thread_safe else None

    def enqueue(self, item: T) -> bool:
        """Add an item to the end of the queue.

        Args:
            item: Item to add

        Returns:
            True if item was added, False if queue is full

        Raises:
            RuntimeError: If queue is at max capacity
        """
        if self._lock:
            with self._lock:
                return self._enqueue_unsafe(item)
        return self._enqueue_unsafe(item)

    def _enqueue_unsafe(self, item: T) -> bool:
        """Unsafe enqueue (must be called with lock held)."""
        if self.max_size is not None and len(self.items) >= self.max_size:
            logger.warning("Queue is full, cannot enqueue item")
            return False
        self.items.append(item)
        logger.debug("Enqueued item, queue size: %d", len(self.items))
        return True

    def dequeue(self) -> Optional[T]:
        """Remove and return the first item in the queue.

        Returns:
            First item in queue, or None if queue is empty
        """
        if self._lock:
            with self._lock:
                return self._dequeue_unsafe()
        return self._dequeue_unsafe()

    def _dequeue_unsafe(self) -> Optional[T]:
        """Unsafe dequeue (must be called with lock held)."""
        if len(self.items) == 0:
            return None
        item = self.items.popleft()
        logger.debug("Dequeued item, queue size: %d", len(self.items))
        return item

    def peek(self) -> Optional[T]:
        """View the first item without removing it.

        Returns:
            First item in queue, or None if queue is empty
        """
        if self._lock:
            with self._lock:
                return self._peek_unsafe()
        return self._peek_unsafe()

    def _peek_unsafe(self) -> Optional[T]:
        """Unsafe peek (must be called with lock held)."""
        return self.items[0] if len(self.items) > 0 else None

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        if self._lock:
            with self._lock:
                return len(self.items) == 0
        return len(self.items) == 0

    def is_full(self) -> bool:
        """Check if queue is at maximum capacity."""
        if self.max_size is None:
            return False
        if self._lock:
            with self._lock:
                return len(self.items) >= self.max_size
        return len(self.items) >= self.max_size

    def size(self) -> int:
        """Get the current number of items in queue."""
        if self._lock:
            with self._lock:
                return len(self.items)
        return len(self.items)

    def clear(self) -> None:
        """Remove all items from the queue."""
        if self._lock:
            with self._lock:
                self.items.clear()
        else:
            self.items.clear()
        logger.debug("Queue cleared")

    def __len__(self) -> int:
        """Return the number of items in queue."""
        return self.size()

    def __iter__(self) -> Iterator[T]:
        """Iterate over queue items (FIFO order)."""
        if self._lock:
            with self._lock:
                # Create copy to iterate safely
                return iter(list(self.items))
        return iter(self.items)

    def __repr__(self) -> str:
        """String representation."""
        return f"Queue(size={self.size()}, max_size={self.max_size})"

    def __str__(self) -> str:
        """Human-readable representation."""
        items_list = list(self.items)
        if len(items_list) == 0:
            return "Queue(empty)"
        return f"Queue({len(items_list)} items)"


class PriorityQueue(Generic[T]):
    """A priority-based queue where items are processed by priority.

    Items with higher priority (lower priority value) are dequeued first.

    Attributes:
        items: List of items sorted by priority
        thread_lock: Lock for thread-safe operations
    """

    def __init__(self, thread_safe: bool = False) -> None:
        """Initialize a priority queue.

        Args:
            thread_safe: Enable thread-safe operations with locks
        """
        self.items: List[T] = []
        self.thread_safe = thread_safe
        self._lock = threading.Lock() if thread_safe else None

    def enqueue(self, item: T) -> None:
        """Add an item to the queue in priority order.

        Args:
            item: Item to add (must implement __lt__ for comparison)
        """
        if self._lock:
            with self._lock:
                self._enqueue_unsafe(item)
        else:
            self._enqueue_unsafe(item)

    def _enqueue_unsafe(self, item: T) -> None:
        """Unsafe enqueue (must be called with lock held)."""
        # Find correct position based on priority
        inserted = False
        for i, existing_item in enumerate(self.items):
            if item < existing_item:
                self.items.insert(i, item)
                inserted = True
                break
        if not inserted:
            self.items.append(item)
        logger.debug("Enqueued prioritized item, queue size: %d", len(self.items))

    def dequeue(self) -> Optional[T]:
        """Remove and return the highest priority item.

        Returns:
            Highest priority item, or None if queue is empty
        """
        if self._lock:
            with self._lock:
                return self._dequeue_unsafe()
        return self._dequeue_unsafe()

    def _dequeue_unsafe(self) -> Optional[T]:
        """Unsafe dequeue (must be called with lock held)."""
        if len(self.items) == 0:
            return None
        item = self.items.pop(0)
        logger.debug("Dequeued prioritized item, queue size: %d", len(self.items))
        return item

    def peek(self) -> Optional[T]:
        """View the highest priority item without removing it.

        Returns:
            Highest priority item, or None if queue is empty
        """
        if self._lock:
            with self._lock:
                return self._peek_unsafe()
        return self._peek_unsafe()

    def _peek_unsafe(self) -> Optional[T]:
        """Unsafe peek (must be called with lock held)."""
        return self.items[0] if len(self.items) > 0 else None

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        if self._lock:
            with self._lock:
                return len(self.items) == 0
        return len(self.items) == 0

    def size(self) -> int:
        """Get the current number of items in queue."""
        if self._lock:
            with self._lock:
                return len(self.items)
        return len(self.items)

    def clear(self) -> None:
        """Remove all items from the queue."""
        if self._lock:
            with self._lock:
                self.items.clear()
        else:
            self.items.clear()
        logger.debug("Priority queue cleared")

    def __len__(self) -> int:
        """Return the number of items in queue."""
        return self.size()

    def __iter__(self) -> Iterator[T]:
        """Iterate over queue items in priority order."""
        if self._lock:
            with self._lock:
                return iter(list(self.items))
        return iter(self.items)

    def __repr__(self) -> str:
        """String representation."""
        return f"PriorityQueue(size={self.size()})"

    def __str__(self) -> str:
        """Human-readable representation."""
        if len(self.items) == 0:
            return "PriorityQueue(empty)"
        return f"PriorityQueue({len(self.items)} items)"


class ExtractionQueue:
    """A specialized queue for managing weather data extraction tasks.

    Manages a priority queue of extraction tasks with status tracking,
    retry logic, and result storage.

    Attributes:
        tasks_queue: Priority queue of pending tasks
        completed_tasks: Dictionary of completed tasks
        failed_tasks: Dictionary of failed tasks
        thread_safe: Whether operations are thread-safe
    """

    def __init__(self, thread_safe: bool = True) -> None:
        """Initialize extraction queue.

        Args:
            thread_safe: Enable thread-safe operations
        """
        self.tasks_queue: PriorityQueue[ExtractionTask] = PriorityQueue(thread_safe=thread_safe)
        self.completed_tasks: dict[str, ExtractionTask] = {}
        self.failed_tasks: dict[str, ExtractionTask] = {}
        self.processing_tasks: dict[str, ExtractionTask] = {}
        self.thread_safe = thread_safe
        self._lock = threading.Lock() if thread_safe else None

    def add_task(self, task: ExtractionTask) -> bool:
        """Add an extraction task to the queue.

        Args:
            task: Task to add

        Returns:
            True if task was added successfully
        """
        if task.status != TaskStatus.PENDING:
            logger.warning("Task %s is not in PENDING status", task.task_id)
            return False

        self.tasks_queue.enqueue(task)
        logger.info("Added task %s to extraction queue", task.task_id)
        return True

    def get_next_task(self) -> Optional[ExtractionTask]:
        """Get the next task from the queue.

        Returns:
            Next highest priority task, or None if queue is empty
        """
        task = self.tasks_queue.dequeue()
        if task:
            task.status = TaskStatus.PROCESSING
            if self._lock:
                with self._lock:
                    self.processing_tasks[task.task_id] = task
            else:
                self.processing_tasks[task.task_id] = task
            logger.info("Got next task: %s", task.task_id)
        return task

    def complete_task(self, task_id: str, result: pd.DataFrame) -> bool:
        """Mark a task as completed with result.

        Args:
            task_id: ID of the task
            result: DataFrame result of extraction

        Returns:
            True if task was completed successfully
        """
        if self._lock:
            with self._lock:
                return self._complete_task_unsafe(task_id, result)
        return self._complete_task_unsafe(task_id, result)

    def _complete_task_unsafe(self, task_id: str, result: pd.DataFrame) -> bool:
        """Unsafe complete task (must be called with lock held)."""
        if task_id not in self.processing_tasks:
            logger.warning("Task %s not in processing", task_id)
            return False

        task = self.processing_tasks.pop(task_id)
        task.status = TaskStatus.COMPLETED
        task.result = result
        self.completed_tasks[task_id] = task
        logger.info("Completed task %s", task_id)
        return True

    def fail_task(self, task_id: str, error_message: str, retry: bool = True) -> bool:
        """Mark a task as failed.

        Args:
            task_id: ID of the task
            error_message: Description of the failure
            retry: Whether to retry the task

        Returns:
            True if task should be retried, False otherwise
        """
        if self._lock:
            with self._lock:
                return self._fail_task_unsafe(task_id, error_message, retry)
        return self._fail_task_unsafe(task_id, error_message, retry)

    def _fail_task_unsafe(
        self, task_id: str, error_message: str, retry: bool = True
    ) -> bool:
        """Unsafe fail task (must be called with lock held)."""
        if task_id not in self.processing_tasks:
            logger.warning("Task %s not in processing", task_id)
            return False

        task = self.processing_tasks.pop(task_id)
        task.error_message = error_message
        task.retry_count += 1

        if retry and task.retry_count < task.max_retries:
            # Re-add to queue for retry
            task.status = TaskStatus.PENDING
            self.tasks_queue.enqueue(task)
            logger.info("Task %s will be retried (%d/%d)", 
                       task_id, task.retry_count, task.max_retries)
            return True
        else:
            # Move to failed
            task.status = TaskStatus.FAILED
            self.failed_tasks[task_id] = task
            logger.error("Task %s permanently failed", task_id)
            return False

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task.

        Args:
            task_id: ID of the task

        Returns:
            Task status, or None if task not found
        """
        if task_id in self.processing_tasks:
            return self.processing_tasks[task_id].status
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].status
        if task_id in self.failed_tasks:
            return self.failed_tasks[task_id].status
        if not self.tasks_queue.is_empty():
            for task in self.tasks_queue:
                if task.task_id == task_id:
                    return task.status
        return None

    def get_task_result(self, task_id: str) -> Optional[pd.DataFrame]:
        """Get the result of a completed task.

        Args:
            task_id: ID of the task

        Returns:
            DataFrame result if completed, None otherwise
        """
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].result
        return None

    def get_pending_count(self) -> int:
        """Get the number of pending tasks."""
        return self.tasks_queue.size()

    def get_processing_count(self) -> int:
        """Get the number of tasks currently being processed."""
        if self._lock:
            with self._lock:
                return len(self.processing_tasks)
        return len(self.processing_tasks)

    def get_completed_count(self) -> int:
        """Get the number of completed tasks."""
        if self._lock:
            with self._lock:
                return len(self.completed_tasks)
        return len(self.completed_tasks)

    def get_failed_count(self) -> int:
        """Get the number of failed tasks."""
        if self._lock:
            with self._lock:
                return len(self.failed_tasks)
        return len(self.failed_tasks)

    def get_stats(self) -> dict:
        """Get extraction queue statistics.

        Returns:
            Dictionary with queue statistics
        """
        return {
            'pending': self.get_pending_count(),
            'processing': self.get_processing_count(),
            'completed': self.get_completed_count(),
            'failed': self.get_failed_count(),
            'total': (self.get_pending_count() + self.get_processing_count() +
                     self.get_completed_count() + self.get_failed_count()),
        }

    def get_all_tasks(self) -> dict[str, list[ExtractionTask]]:
        """Get all tasks organized by status.

        Returns:
            Dictionary with tasks organized by status
        """
        if self._lock:
            with self._lock:
                return self._get_all_tasks_unsafe()
        return self._get_all_tasks_unsafe()

    def _get_all_tasks_unsafe(self) -> dict[str, list[ExtractionTask]]:
        """Unsafe get all tasks (must be called with lock held)."""
        pending = list(self.tasks_queue)
        return {
            'pending': pending,
            'processing': list(self.processing_tasks.values()),
            'completed': list(self.completed_tasks.values()),
            'failed': list(self.failed_tasks.values()),
        }

    def clear(self) -> None:
        """Clear all tasks from the queue."""
        if self._lock:
            with self._lock:
                self.tasks_queue.clear()
                self.completed_tasks.clear()
                self.failed_tasks.clear()
                self.processing_tasks.clear()
        else:
            self.tasks_queue.clear()
            self.completed_tasks.clear()
            self.failed_tasks.clear()
            self.processing_tasks.clear()
        logger.info("Extraction queue cleared")

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return f"ExtractionQueue(pending={stats['pending']}, completed={stats['completed']})"

    def __str__(self) -> str:
        """Human-readable representation."""
        stats = self.get_stats()
        return (
            f"ExtractionQueue: {stats['pending']} pending, "
            f"{stats['processing']} processing, "
            f"{stats['completed']} completed, "
            f"{stats['failed']} failed"
        )
