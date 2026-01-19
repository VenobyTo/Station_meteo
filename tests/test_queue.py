"""Tests for queue module."""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from threading import Thread
import time

from projet.queue import (
    Queue, PriorityQueue, ExtractionQueue, ExtractionTask,
    TaskStatus, TaskPriority
)


class TestQueue:
    """Tests for FIFO Queue."""

    def test_queue_creation(self):
        """Test queue creation."""
        queue = Queue()
        assert queue.is_empty()
        assert queue.size() == 0

    def test_queue_enqueue(self):
        """Test enqueue operation."""
        queue = Queue()
        assert queue.enqueue(1)
        assert queue.enqueue(2)
        assert queue.size() == 2

    def test_queue_dequeue(self):
        """Test dequeue operation (FIFO order)."""
        queue = Queue()
        queue.enqueue(1)
        queue.enqueue(2)
        queue.enqueue(3)

        assert queue.dequeue() == 1
        assert queue.dequeue() == 2
        assert queue.dequeue() == 3
        assert queue.dequeue() is None

    def test_queue_peek(self):
        """Test peek operation."""
        queue = Queue()
        queue.enqueue(1)
        queue.enqueue(2)

        assert queue.peek() == 1
        assert queue.size() == 2  # Peek doesn't remove

    def test_queue_is_empty(self):
        """Test is_empty check."""
        queue = Queue()
        assert queue.is_empty()
        queue.enqueue(1)
        assert not queue.is_empty()
        queue.dequeue()
        assert queue.is_empty()

    def test_queue_max_size(self):
        """Test queue with max size."""
        queue = Queue(max_size=2)
        assert queue.enqueue(1)
        assert queue.enqueue(2)
        assert not queue.enqueue(3)  # Should fail, queue is full
        assert queue.size() == 2

    def test_queue_clear(self):
        """Test clear operation."""
        queue = Queue()
        queue.enqueue(1)
        queue.enqueue(2)
        queue.clear()
        assert queue.is_empty()

    def test_queue_iteration(self):
        """Test queue iteration."""
        queue = Queue()
        queue.enqueue(1)
        queue.enqueue(2)
        queue.enqueue(3)

        items = list(queue)
        assert items == [1, 2, 3]

    def test_queue_len(self):
        """Test len() on queue."""
        queue = Queue()
        assert len(queue) == 0
        queue.enqueue(1)
        assert len(queue) == 1
        queue.enqueue(2)
        assert len(queue) == 2

    def test_queue_repr(self):
        """Test string representation."""
        queue = Queue(max_size=5)
        queue.enqueue(1)
        assert "Queue" in repr(queue)
        assert "max_size=5" in repr(queue)

    def test_queue_thread_safe(self):
        """Test thread-safe queue operations."""
        queue = Queue(thread_safe=True)
        results = []

        def enqueuer():
            for i in range(100):
                queue.enqueue(i)

        def dequeuer():
            for _ in range(100):
                item = queue.dequeue()
                if item is not None:
                    results.append(item)

        t1 = Thread(target=enqueuer)
        t2 = Thread(target=dequeuer)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        assert len(results) == 100


class TestPriorityQueue:
    """Tests for priority queue."""

    def test_priority_queue_creation(self):
        """Test priority queue creation."""
        pq = PriorityQueue()
        assert pq.is_empty()

    def test_priority_queue_enqueue(self):
        """Test enqueue with priorities."""
        pq = PriorityQueue()
        
        task1 = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31",
                              priority=TaskPriority.LOW)
        task2 = ExtractionTask("2", "s2", "Station 2", "2024-01-01", "2024-01-31",
                              priority=TaskPriority.HIGH)
        task3 = ExtractionTask("3", "s3", "Station 3", "2024-01-01", "2024-01-31",
                              priority=TaskPriority.NORMAL)

        pq.enqueue(task1)
        pq.enqueue(task2)
        pq.enqueue(task3)

        # Should dequeue in priority order: HIGH, NORMAL, LOW
        assert pq.dequeue().task_id == "2"
        assert pq.dequeue().task_id == "3"
        assert pq.dequeue().task_id == "1"

    def test_priority_queue_same_priority_fifo(self):
        """Test FIFO order for items with same priority."""
        pq = PriorityQueue()
        
        task1 = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31",
                              priority=TaskPriority.NORMAL)
        task2 = ExtractionTask("2", "s2", "Station 2", "2024-01-01", "2024-01-31",
                              priority=TaskPriority.NORMAL)

        pq.enqueue(task1)
        pq.enqueue(task2)

        # Same priority, so FIFO: task1 first
        assert pq.dequeue().task_id == "1"
        assert pq.dequeue().task_id == "2"

    def test_priority_queue_peek(self):
        """Test peek on priority queue."""
        pq = PriorityQueue()
        
        task1 = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31",
                              priority=TaskPriority.LOW)
        task2 = ExtractionTask("2", "s2", "Station 2", "2024-01-01", "2024-01-31",
                              priority=TaskPriority.HIGH)

        pq.enqueue(task1)
        pq.enqueue(task2)

        # Peek should return high priority task without removing
        assert pq.peek().task_id == "2"
        assert pq.size() == 2

    def test_priority_queue_clear(self):
        """Test clear on priority queue."""
        pq = PriorityQueue()
        pq.enqueue(ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31"))
        pq.clear()
        assert pq.is_empty()

    def test_priority_queue_iteration(self):
        """Test iteration over priority queue."""
        pq = PriorityQueue()
        tasks = [
            ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31",
                          priority=TaskPriority.LOW),
            ExtractionTask("2", "s2", "Station 2", "2024-01-01", "2024-01-31",
                          priority=TaskPriority.HIGH),
        ]
        for task in tasks:
            pq.enqueue(task)

        items = list(pq)
        assert len(items) == 2


class TestExtractionTask:
    """Tests for ExtractionTask."""

    def test_task_creation(self):
        """Test task creation."""
        task = ExtractionTask(
            "task1", "station1", "Paris", "2024-01-01", "2024-01-31"
        )
        assert task.task_id == "task1"
        assert task.station_id == "station1"
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 0

    def test_task_priority_comparison(self):
        """Test task priority comparison."""
        task1 = ExtractionTask("1", "s1", "S1", "2024-01-01", "2024-01-31",
                              priority=TaskPriority.LOW)
        task2 = ExtractionTask("2", "s2", "S2", "2024-01-01", "2024-01-31",
                              priority=TaskPriority.HIGH)
        
        # HIGH priority should be "less than" LOW priority (higher priority)
        assert task2 < task1

    def test_task_to_dict(self):
        """Test task to_dict conversion."""
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31")
        d = task.to_dict()
        
        assert d['task_id'] == "1"
        assert d['station_id'] == "s1"
        assert d['station_name'] == "Station 1"
        assert d['status'] == "pending"

    def test_task_repr(self):
        """Test task repr."""
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31")
        repr_str = repr(task)
        assert "ExtractionTask" in repr_str
        assert "id=1" in repr_str

    def test_task_str(self):
        """Test task str."""
        task = ExtractionTask("task1", "s1", "Paris", "2024-01-01", "2024-01-31")
        str_repr = str(task)
        assert "task1" in str_repr
        assert "Paris" in str_repr


class TestExtractionQueue:
    """Tests for ExtractionQueue."""

    def test_extraction_queue_creation(self):
        """Test extraction queue creation."""
        eq = ExtractionQueue()
        assert eq.get_pending_count() == 0
        assert eq.get_completed_count() == 0

    def test_extraction_queue_add_task(self):
        """Test adding tasks to extraction queue."""
        eq = ExtractionQueue()
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31")
        
        assert eq.add_task(task)
        assert eq.get_pending_count() == 1

    def test_extraction_queue_get_next_task(self):
        """Test getting next task."""
        eq = ExtractionQueue()
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31")
        eq.add_task(task)

        next_task = eq.get_next_task()
        assert next_task is not None
        assert next_task.task_id == "1"
        assert next_task.status == TaskStatus.PROCESSING
        assert eq.get_processing_count() == 1
        assert eq.get_pending_count() == 0

    def test_extraction_queue_complete_task(self):
        """Test completing a task."""
        eq = ExtractionQueue()
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31")
        eq.add_task(task)

        next_task = eq.get_next_task()
        df = pd.DataFrame({'temp': [20, 21, 22]})
        
        assert eq.complete_task(next_task.task_id, df)
        assert eq.get_completed_count() == 1
        assert eq.get_processing_count() == 0
        
        # Check result can be retrieved
        result = eq.get_task_result("1")
        assert result is not None
        assert len(result) == 3

    def test_extraction_queue_fail_task_with_retry(self):
        """Test failing a task with retry."""
        eq = ExtractionQueue()
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31",
                             max_retries=3)
        eq.add_task(task)

        next_task = eq.get_next_task()
        assert eq.fail_task(next_task.task_id, "Connection error", retry=True)
        
        # Task should be back in pending for retry
        assert eq.get_pending_count() == 1
        assert eq.get_processing_count() == 0
        assert eq.get_failed_count() == 0

    def test_extraction_queue_fail_task_permanent(self):
        """Test permanently failing a task."""
        eq = ExtractionQueue()
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31",
                             max_retries=2)
        eq.add_task(task)

        # First attempt - fail and should retry (retry_count becomes 1, 1 < 2)
        next_task = eq.get_next_task()
        assert next_task is not None
        assert next_task.retry_count == 0
        result = eq.fail_task(next_task.task_id, "Error 1", retry=True)
        assert result  # Should retry since retry_count becomes 1, 1 < max_retries (2)
        
        # Second attempt - fail and should retry (retry_count becomes 2, 2 < 2 is False)
        next_task = eq.get_next_task()
        assert next_task is not None
        assert next_task.retry_count == 1
        result = eq.fail_task(next_task.task_id, "Error 2", retry=True)
        assert not result  # Should NOT retry since retry_count becomes 2, 2 < max_retries (2) is False
        
        # Task should now be in failed
        assert eq.get_failed_count() == 1
        assert eq.get_processing_count() == 0
        assert eq.get_pending_count() == 0

    def test_extraction_queue_get_task_status(self):
        """Test getting task status."""
        eq = ExtractionQueue()
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31")
        eq.add_task(task)

        assert eq.get_task_status("1") == TaskStatus.PENDING
        
        eq.get_next_task()
        assert eq.get_task_status("1") == TaskStatus.PROCESSING

    def test_extraction_queue_get_stats(self):
        """Test getting queue statistics."""
        eq = ExtractionQueue()
        task1 = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31")
        task2 = ExtractionTask("2", "s2", "Station 2", "2024-01-01", "2024-01-31")
        
        eq.add_task(task1)
        eq.add_task(task2)

        stats = eq.get_stats()
        assert stats['pending'] == 2
        assert stats['completed'] == 0
        assert stats['total'] == 2

    def test_extraction_queue_get_all_tasks(self):
        """Test getting all tasks organized by status."""
        eq = ExtractionQueue()
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31")
        eq.add_task(task)

        all_tasks = eq.get_all_tasks()
        assert len(all_tasks['pending']) == 1
        assert len(all_tasks['completed']) == 0

    def test_extraction_queue_priority_order(self):
        """Test tasks are processed by priority."""
        eq = ExtractionQueue()
        
        task_low = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31",
                                  priority=TaskPriority.LOW)
        task_high = ExtractionTask("2", "s2", "Station 2", "2024-01-01", "2024-01-31",
                                   priority=TaskPriority.HIGH)
        
        eq.add_task(task_low)
        eq.add_task(task_high)

        # Should get high priority task first
        first = eq.get_next_task()
        assert first.task_id == "2"
        
        second = eq.get_next_task()
        assert second.task_id == "1"

    def test_extraction_queue_clear(self):
        """Test clearing the queue."""
        eq = ExtractionQueue()
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31")
        eq.add_task(task)

        eq.clear()
        assert eq.get_pending_count() == 0
        assert eq.get_completed_count() == 0

    def test_extraction_queue_thread_safe(self):
        """Test thread-safe extraction queue."""
        eq = ExtractionQueue(thread_safe=True)
        
        def add_tasks():
            for i in range(50):
                task = ExtractionTask(
                    f"task{i}", f"s{i}", f"Station {i}",
                    "2024-01-01", "2024-01-31"
                )
                eq.add_task(task)

        def process_tasks():
            for _ in range(50):
                task = eq.get_next_task()
                if task:
                    df = pd.DataFrame({'temp': [20]})
                    eq.complete_task(task.task_id, df)

        t1 = Thread(target=add_tasks)
        t2 = Thread(target=process_tasks)

        t1.start()
        time.sleep(0.1)  # Let some tasks be added first
        t2.start()

        t1.join()
        t2.join()

        stats = eq.get_stats()
        assert stats['completed'] + stats['pending'] == 50

    def test_extraction_queue_repr(self):
        """Test extraction queue repr."""
        eq = ExtractionQueue()
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31")
        eq.add_task(task)

        repr_str = repr(eq)
        assert "ExtractionQueue" in repr_str

    def test_extraction_queue_str(self):
        """Test extraction queue str."""
        eq = ExtractionQueue()
        task = ExtractionTask("1", "s1", "Station 1", "2024-01-01", "2024-01-31")
        eq.add_task(task)

        str_repr = str(eq)
        assert "1 pending" in str_repr
