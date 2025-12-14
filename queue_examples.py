"""Examples of queue usage for weather data extraction."""

import pandas as pd
from datetime import datetime, timedelta
from projet.queue import (
    Queue, PriorityQueue, ExtractionQueue, ExtractionTask,
    TaskStatus, TaskPriority
)


def example1_basic_fifo_queue():
    """Example 1: Basic FIFO queue operations."""
    print("\n" + "="*60)
    print("Example 1: Basic FIFO Queue Operations")
    print("="*60)

    # Create a simple FIFO queue
    queue = Queue()
    print(f"Created queue: {queue}")

    # Enqueue items
    print("\nEnqueueing items: 1, 2, 3, 4, 5")
    for i in range(1, 6):
        queue.enqueue(i)
    print(f"Queue size: {len(queue)}")
    print(f"Queue peek: {queue.peek()}")

    # Dequeue items (FIFO order)
    print("\nDequeueing items:")
    while not queue.is_empty():
        item = queue.dequeue()
        print(f"  Dequeued: {item}, remaining: {len(queue)}")

    print(f"Final state: {queue}")


def example2_priority_queue():
    """Example 2: Priority queue with weather tasks."""
    print("\n" + "="*60)
    print("Example 2: Priority Queue with Different Priorities")
    print("="*60)

    pq = PriorityQueue()
    print(f"Created priority queue: {pq}")

    # Create tasks with different priorities
    print("\nCreating tasks with different priorities:")
    tasks = [
        ExtractionTask("task_low", "s1", "Paris", "2024-01-01", "2024-01-31",
                      priority=TaskPriority.LOW),
        ExtractionTask("task_normal", "s2", "Lyon", "2024-01-01", "2024-01-31",
                      priority=TaskPriority.NORMAL),
        ExtractionTask("task_urgent", "s3", "Marseille", "2024-01-01", "2024-01-31",
                      priority=TaskPriority.URGENT),
        ExtractionTask("task_high", "s4", "Toulouse", "2024-01-01", "2024-01-31",
                      priority=TaskPriority.HIGH),
    ]

    for task in tasks:
        pq.enqueue(task)
        print(f"  Enqueued: {task}")

    # Dequeue in priority order
    print("\nDequeueing in priority order:")
    while not pq.is_empty():
        task = pq.dequeue()
        print(f"  {task.task_id}: {task.station_name} ({task.priority.name})")


def example3_extraction_queue():
    """Example 3: Extraction queue with full lifecycle."""
    print("\n" + "="*60)
    print("Example 3: Extraction Queue - Full Task Lifecycle")
    print("="*60)

    eq = ExtractionQueue()
    print(f"Created extraction queue: {eq}")

    # Add multiple tasks
    print("\nAdding 5 extraction tasks:")
    for i in range(1, 6):
        task = ExtractionTask(
            f"task_{i}", f"station_{i}", f"City {i}",
            "2024-01-01", "2024-01-31",
            priority=TaskPriority.NORMAL
        )
        eq.add_task(task)
        print(f"  Added: {task}")

    stats = eq.get_stats()
    print(f"\nQueue stats: {stats}")

    # Process tasks
    print("\nProcessing tasks:")
    completed = 0
    for i in range(5):
        task = eq.get_next_task()
        if task:
            print(f"  Processing: {task.task_id}")
            
            # Simulate result
            df = pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=30),
                'temperature': [20 + i for _ in range(30)],
                'humidity': [60 + i for _ in range(30)]
            })
            
            eq.complete_task(task.task_id, df)
            print(f"    ✓ Completed: {task.task_id}")
            completed += 1

    stats = eq.get_stats()
    print(f"\nFinal stats: {stats}")


def example4_task_retry_mechanism():
    """Example 4: Task retry mechanism with failures."""
    print("\n" + "="*60)
    print("Example 4: Task Retry Mechanism")
    print("="*60)

    eq = ExtractionQueue()
    print("Created extraction queue with retry mechanism\n")

    # Create a task with 3 max retries
    task = ExtractionTask(
        "retry_task", "station_1", "Paris",
        "2024-01-01", "2024-01-31",
        max_retries=3
    )
    eq.add_task(task)
    print(f"Added task: {task}")
    print(f"Max retries: {task.max_retries}")

    # Simulate failures with retries
    print("\nSimulating failures and retries:")
    for attempt in range(4):
        task = eq.get_next_task()
        if not task:
            print("  No more tasks to process")
            break

        print(f"\n  Attempt {attempt + 1}:")
        print(f"    Processing: {task.task_id}")
        
        if attempt < 3:
            # Fail and retry
            will_retry = eq.fail_task(task.task_id, "Connection timeout", retry=True)
            print(f"    ✗ Failed: Connection timeout")
            print(f"    → Will retry: {will_retry} (retry {task.retry_count}/3)")
        else:
            # Permanent failure
            will_retry = eq.fail_task(task.task_id, "Max retries exceeded", retry=True)
            print(f"    ✗ Permanently failed: Max retries exceeded")
            print(f"    → Will retry: {will_retry}")

    # Check final state
    stats = eq.get_stats()
    print(f"\nFinal stats: {stats}")
    print(f"Failed tasks: {eq.get_failed_count()}")


def example5_advanced_task_management():
    """Example 5: Advanced task management and monitoring."""
    print("\n" + "="*60)
    print("Example 5: Advanced Task Management")
    print("="*60)

    eq = ExtractionQueue()

    # Create tasks with mixed priorities
    print("Creating mixed priority tasks:")
    task_configs = [
        ("task_1", "Paris", TaskPriority.NORMAL),
        ("task_2", "Lyon", TaskPriority.HIGH),
        ("task_3", "Marseille", TaskPriority.LOW),
        ("task_4", "Toulouse", TaskPriority.URGENT),
        ("task_5", "Nice", TaskPriority.NORMAL),
    ]

    for task_id, city, priority in task_configs:
        task = ExtractionTask(
            task_id, task_id.replace("task_", "s"), city,
            "2024-01-01", "2024-12-31",
            priority=priority
        )
        eq.add_task(task)
        print(f"  {task_id}: {city} ({priority.name})")

    # Process in priority order
    print("\nProcessing tasks in priority order:")
    order = []
    while not eq.tasks_queue.is_empty():
        task = eq.get_next_task()
        if task:
            order.append(task.task_id)
            
            # Simulate processing
            df = pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=365),
                'temperature': [15 + i*0.01 for i in range(365)],
            })
            eq.complete_task(task.task_id, df)
            print(f"  {task.task_id}: Completed")

    print(f"\nProcessing order: {' → '.join(order)}")

    # Display final report
    stats = eq.get_stats()
    print(f"\nFinal Report:")
    print(f"  Completed: {stats['completed']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Total: {stats['total']}")

    # Show task details
    all_tasks = eq.get_all_tasks()
    print(f"\nCompleted tasks ({len(all_tasks['completed'])}):")
    for task in all_tasks['completed']:
        result = eq.get_task_result(task.task_id)
        rows = len(result) if result is not None else 0
        print(f"  {task.task_id}: {task.station_name} - {rows} records")


if __name__ == "__main__":
    print("\n" + "█"*60)
    print("█  Queue Examples - Weather Data Extraction")
    print("█"*60)

    example1_basic_fifo_queue()
    example2_priority_queue()
    example3_extraction_queue()
    example4_task_retry_mechanism()
    example5_advanced_task_management()

    print("\n" + "█"*60)
    print("█  All examples completed successfully!")
    print("█"*60 + "\n")
