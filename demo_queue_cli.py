#!/usr/bin/env python3
"""Demo script showing CLI integration of extraction queue."""

import time
import pandas as pd
from projet.queue import (
    ExtractionQueue, ExtractionTask,
    TaskStatus, TaskPriority
)


def demo_extraction_queue_with_cli():
    """Demonstrate extraction queue usage for CLI integration."""
    
    print("\n" + "="*70)
    print("EXTRACTION QUEUE - CLI Integration Demo")
    print("="*70)
    
    # Simulate CLI input for extraction tasks
    stations_config = [
        {
            'station_id': 'PARIS_01',
            'station_name': 'Paris - Montsouris',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'priority': TaskPriority.HIGH,
        },
        {
            'station_id': 'LYON_01',
            'station_name': 'Lyon - Brotteaux',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'priority': TaskPriority.NORMAL,
        },
        {
            'station_id': 'MARSEILLE_01',
            'station_name': 'Marseille - Aeroport',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'priority': TaskPriority.HIGH,
        },
        {
            'station_id': 'TOULOUSE_01',
            'station_name': 'Toulouse - Francazal',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'priority': TaskPriority.NORMAL,
        },
    ]
    
    # Create extraction queue
    eq = ExtractionQueue(thread_safe=False)
    
    print("\n1️⃣  CREATING EXTRACTION TASKS")
    print("-" * 70)
    for i, config in enumerate(stations_config, 1):
        task = ExtractionTask(
            task_id=f"task_{i:03d}",
            station_id=config['station_id'],
            station_name=config['station_name'],
            start_date=config['start_date'],
            end_date=config['end_date'],
            source='toulouse',
            priority=config['priority'],
            max_retries=2
        )
        eq.add_task(task)
        print(f"  ✓ Created: {task.station_id} ({task.priority.name})")
    
    # Show initial stats
    stats = eq.get_stats()
    print(f"\n  Total tasks queued: {stats['total']}")
    print(f"  Pending: {stats['pending']}")
    
    # Process tasks
    print("\n2️⃣  PROCESSING EXTRACTION QUEUE")
    print("-" * 70)
    
    processed = 0
    failed = 0
    
    while eq.get_pending_count() > 0:
        # Get next task
        task = eq.get_next_task()
        if not task:
            break
        
        processed += 1
        print(f"\n  Task {processed}: {task.station_id}")
        print(f"    Status: {task.status.value}")
        print(f"    Period: {task.start_date} to {task.end_date}")
        print(f"    Priority: {task.priority.name}")
        
        # Simulate extraction with occasional failures
        import random
        should_fail = random.random() < 0.2  # 20% failure rate
        
        if should_fail and task.retry_count < 1:
            # Simulate failure with retry
            print(f"    ⚠️  Simulated error: Connection timeout")
            will_retry = eq.fail_task(task.task_id, "Connection timeout", retry=True)
            print(f"    ↻  Retrying... ({task.retry_count + 1}/{task.max_retries})")
        else:
            # Simulate successful extraction
            try:
                # Create mock data
                dates = pd.date_range(task.start_date, task.end_date, freq='D')
                df = pd.DataFrame({
                    'date': dates,
                    'temperature': [15 + i*0.01 for i in range(len(dates))],
                    'humidity': [60 + i*0.05 for i in range(len(dates))],
                    'pressure': [1013 + i*0.001 for i in range(len(dates))],
                })
                
                eq.complete_task(task.task_id, df)
                print(f"    ✅ Completed: {len(df)} records extracted")
            except Exception as e:
                failed += 1
                print(f"    ❌ Error: {str(e)}")
                eq.fail_task(task.task_id, str(e), retry=True)
    
    # Final report
    print("\n3️⃣  EXTRACTION REPORT")
    print("-" * 70)
    
    stats = eq.get_stats()
    all_tasks = eq.get_all_tasks()
    
    print(f"\n  Summary:")
    print(f"    ✅ Completed: {stats['completed']}")
    print(f"    ⏳ Processing: {stats['processing']}")
    print(f"    ⏳ Pending: {stats['pending']}")
    print(f"    ❌ Failed: {stats['failed']}")
    print(f"    📊 Total: {stats['total']}")
    
    if all_tasks['completed']:
        print(f"\n  Completed Stations:")
        for task in all_tasks['completed']:
            result = eq.get_task_result(task.task_id)
            if result is not None:
                print(f"    • {task.station_name}: {len(result)} records")
    
    if all_tasks['failed']:
        print(f"\n  Failed Stations:")
        for task in all_tasks['failed']:
            print(f"    • {task.station_name}: {task.error_message}")
    
    print("\n" + "="*70)
    print("✨ Demo completed!")
    print("="*70 + "\n")


def demo_priority_processing():
    """Demo showing priority-based processing order."""
    
    print("\n" + "="*70)
    print("PRIORITY QUEUE DEMO")
    print("="*70)
    
    eq = ExtractionQueue(thread_safe=False)
    
    # Create tasks with different priorities in random order
    tasks_config = [
        ('NORMAL_01', 'City A', TaskPriority.NORMAL),
        ('LOW_01', 'City B', TaskPriority.LOW),
        ('URGENT_01', 'City C', TaskPriority.URGENT),
        ('HIGH_01', 'City D', TaskPriority.HIGH),
        ('NORMAL_02', 'City E', TaskPriority.NORMAL),
    ]
    
    print("\n📋 Adding tasks in this order:")
    for station_id, name, priority in tasks_config:
        task = ExtractionTask(
            f"task_{station_id}", station_id, name,
            "2024-01-01", "2024-12-31",
            priority=priority
        )
        eq.add_task(task)
        print(f"   {station_id:12} ({priority.name:8})")
    
    print("\n⚡ Processing order (by priority):")
    order = []
    while eq.get_pending_count() > 0:
        task = eq.get_next_task()
        if task:
            order.append((task.station_id, task.priority.name))
            print(f"   {task.station_id:12} ({task.priority.name:8})")
            # Complete task
            eq.complete_task(task.task_id, pd.DataFrame({'temp': [20]}))
    
    print("\n" + "="*70)
    print("\n")


def demo_batch_extraction():
    """Demo showing batch extraction workflow."""
    
    print("\n" + "="*70)
    print("BATCH EXTRACTION WORKFLOW")
    print("="*70)
    
    eq = ExtractionQueue(thread_safe=False)
    
    # Create batch of extraction tasks
    batch_size = 8
    print(f"\n📦 Creating batch of {batch_size} extraction tasks...")
    
    for i in range(batch_size):
        task = ExtractionTask(
            f"batch_task_{i:02d}",
            f"STATION_{i:02d}",
            f"Station {i}",
            "2024-01-01",
            "2024-12-31",
            priority=TaskPriority.NORMAL if i % 2 == 0 else TaskPriority.HIGH
        )
        eq.add_task(task)
    
    print(f"✓ Queued {eq.get_stats()['total']} tasks")
    
    # Process batch with progress tracking
    print(f"\n🔄 Processing batch ({batch_size} tasks)...")
    start_time = time.time()
    
    completed = []
    failed_list = []
    
    while eq.get_pending_count() > 0:
        task = eq.get_next_task()
        if task:
            try:
                # Simulate extraction
                dates = pd.date_range("2024-01-01", "2024-12-31", freq='D')
                df = pd.DataFrame({
                    'date': dates,
                    'temperature': [20 + (i % 30) for i in range(len(dates))],
                    'humidity': [65 for _ in range(len(dates))],
                })
                
                eq.complete_task(task.task_id, df)
                completed.append(task.station_id)
                
                # Progress bar
                progress = len(completed) / batch_size
                bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
                print(f"  [{bar}] {len(completed)}/{batch_size}")
                
            except Exception as e:
                eq.fail_task(task.task_id, str(e), retry=True)
                failed_list.append(task.station_id)
    
    elapsed = time.time() - start_time
    
    # Summary
    stats = eq.get_stats()
    print(f"\n✅ Batch processing completed in {elapsed:.2f}s")
    print(f"  Completed: {stats['completed']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Rate: {stats['completed']/elapsed:.1f} stations/sec")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    demo_extraction_queue_with_cli()
    demo_priority_processing()
    demo_batch_extraction()
    
    print("\n🎉 All demos completed successfully!\n")
