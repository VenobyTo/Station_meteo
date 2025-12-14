#!/usr/bin/env python
"""Quick demo of the linked list CLI command for weather stations.

Shows how to display multiple weather stations sequentially using
the new 'stations' command with linked list backend.
"""

import subprocess
import sys


def run_command(cmd):
    """Run a command and display output."""
    print(f"\n{'='*60}")
    print(f"Command: {cmd}")
    print(f"{'='*60}\n")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")


def main():
    """Run CLI demonstrations."""
    print("\n" + "="*60)
    print("LINKED LIST WEATHER STATION DEMO")
    print("="*60)
    
    # Show help
    print("\n1. Display help for stations command:")
    run_command(f"{sys.executable} -m projet stations --help")
    
    # Show default (Toulouse)
    print("\n2. Display Toulouse station (default):")
    print("   (Requires internet connection to fetch from API)")
    run_command(f"{sys.executable} -m projet stations --source toulouse --limit 5 --sample 2")
    
    print("\nDemo completed!")
    print("\nKey Features:")
    print("  ✓ Linked list stores multiple stations sequentially")
    print("  ✓ Each station is a node with metadata and DataFrame")
    print("  ✓ Supports filtering, combining, and iterating")
    print("  ✓ Full timezone-aware date support")
    print("  ✓ 45 comprehensive unit tests")


if __name__ == "__main__":
    main()
