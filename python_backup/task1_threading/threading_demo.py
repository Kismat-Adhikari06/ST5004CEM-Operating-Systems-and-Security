"""
ST5004CEM - Task 1: Multi-threading
Stage 1: Basic Thread Creation and Execution

This script demonstrates creating and running multiple threads concurrently.
No synchronization primitives are used yet — that comes in later stages.
"""

import threading
import time


def worker(thread_name, duration):
    """
    A simple worker function that each thread will execute.

    In real applications, this is where your thread's actual work would go
    (e.g., processing data, making network calls, reading files).

    Args:
        thread_name: A label to identify which thread is running.
        duration: How long (in seconds) this thread simulates doing work.
    """
    print(f"[{thread_name}] Starting work...")

    # Simulate doing some work by sleeping for the given duration.
    # The thread is still "alive" during sleep — it has been suspended
    # by the OS scheduler and could be resumed at any time.
    time.sleep(duration)

    print(f"[{thread_name}] Finished work (slept for {duration}s).")


def main():
    print("=== Stage 1: Basic Thread Creation and Execution ===\n")

    # Define our workers: each tuple holds (thread_name, work_duration).
    # Different durations let us observe that threads run concurrently,
    # not in sequence — the total runtime is closer to the longest thread,
    # not the sum of all durations.
    workers = [
        ("Thread-A", 2),
        ("Thread-B", 1),
        ("Thread-C", 3),
    ]

    threads = []

    # --- Creating and starting threads ---
    # thread.start() tells the OS to create a new thread of execution.
    # From this point, the new thread runs concurrently alongside the
    # main thread (and any other threads). The OS thread scheduler
    # decides which thread gets CPU time at any given moment.
    print("Creating and starting threads...")
    for name, duration in workers:
        t = threading.Thread(target=worker, args=(name, duration))
        threads.append(t)
        t.start()  # The thread begins executing worker() from here.
        print(f"  -> {name} has been started.")

    print()

    # --- Waiting for threads to finish ---
    # thread.join() blocks the calling thread (main, in this case) until
    # the target thread completes. This is essential when you need to
    # guarantee all threads have finished before proceeding.
    # Without join(), the main thread would print "all threads completed"
    # immediately, before any worker has had a chance to finish.
    print("Main thread waiting for all workers to finish (join)...")
    for t in threads:
        t.join()  # Main thread blocks here until this thread finishes.
        print(f"  -> {t.name} has joined.")

    print()
    print("All threads completed. Main thread exiting.")


if __name__ == "__main__":
    main()
