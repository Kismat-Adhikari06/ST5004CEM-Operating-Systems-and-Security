"""
ST5004CEM - Task 1: Multi-threading
Stage 5: Deadlock Detection and Prevention

Part A: Demonstrates a deadlock scenario using two locks acquired
        in opposite orders, creating a circular wait.
Part B: Shows the fix — acquiring locks in a consistent global order,
        which eliminates the circular wait condition.
"""

import threading
import time


# --- The Four Conditions for Deadlock (Coffman Conditions) ---
#
# Deadlock occurs when ALL FOUR of these conditions hold simultaneously:
#
# 1. Mutual Exclusion: At least one resource must be held in a non-
#    shareable mode. A lock (mutex) is exactly this — only one thread
#    can hold it at a time.
#
# 2. Hold and Wait: A thread holds at least one resource while
#    waiting to acquire additional resources held by other threads.
#
# 3. No Preemption: Resources cannot be forcibly taken from a thread;
#    they must be released voluntarily by the holder.
#
# 4. Circular Wait: A cycle exists in the resource-wait graph.
#    Thread 1 holds lock_a and waits for lock_b, while Thread 2
#    holds lock_b and waits for lock_a.
#
# Deadlock prevention works by breaking AT LEAST ONE of these four
# conditions. The "consistent lock ordering" fix below breaks
# condition 4 (Circular Wait) by ensuring no cycle can form.


# ============================================================================
# PART A: THE PROBLEM — Deadlock via Circular Wait
# ============================================================================

def part_a_thread1(lock_a, lock_b, ready_event):
    """Thread 1: acquires lock_a first, then tries to acquire lock_b."""
    ready_event.wait()  # Synchronize start with Thread 2.

    print("[Part A - Thread 1] Acquiring lock_a...")
    lock_a.acquire()
    print("[Part A - Thread 1] Holding lock_a. Sleeping briefly...")

    time.sleep(0.5)  # Give Thread 2 time to grab lock_b.

    print("[Part A - Thread 1] Trying to acquire lock_b (will timeout if deadlocked)...")
    # Use a timeout so the program doesn't freeze forever.
    # If lock_b is held by Thread 2, this will wait up to 2 seconds,
    # then return False — indicating we could not acquire the lock.
    acquired = lock_b.acquire(timeout=2)
    if acquired:
        print("[Part A - Thread 1] Acquired lock_b. No deadlock.")
        lock_b.release()
    else:
        print("[Part A - Thread 1] TIMEOUT — could not acquire lock_b. Deadlock detected!")

    lock_a.release()
    print("[Part A - Thread 1] Released lock_a. Exiting.\n")


def part_a_thread2(lock_a, lock_b, ready_event):
    """Thread 2: acquires lock_b first, then tries to acquire lock_a."""
    ready_event.wait()  # Synchronize start with Thread 1.

    print("[Part A - Thread 2] Acquiring lock_b...")
    lock_b.acquire()
    print("[Part A - Thread 2] Holding lock_b. Sleeping briefly...")

    time.sleep(0.5)  # Give Thread 1 time to grab lock_a.

    print("[Part A - Thread 2] Trying to acquire lock_a (will timeout if deadlocked)...")
    acquired = lock_a.acquire(timeout=2)
    if acquired:
        print("[Part A - Thread 2] Acquired lock_a. No deadlock.")
        lock_a.release()
    else:
        print("[Part A - Thread 2] TIMEOUT — could not acquire lock_a. Deadlock detected!")

    lock_b.release()
    print("[Part A - Thread 2] Released lock_b. Exiting.\n")


def run_part_a():
    """Demonstrate deadlock caused by circular wait."""
    print("=" * 60)
    print("PART A: DEADLOCK DEMO (Circular Wait)")
    print("=" * 60)
    print("Thread 1: lock_a -> sleep -> lock_b")
    print("Thread 2: lock_b -> sleep -> lock_a")
    print("Opposite acquisition order creates a circular wait.\n")

    lock_a = threading.Lock()
    lock_b = threading.Lock()

    # Both threads start at the same time to maximize the chance of deadlock.
    ready = threading.Event()
    t1 = threading.Thread(target=part_a_thread1, args=(lock_a, lock_b, ready))
    t2 = threading.Thread(target=part_a_thread2, args=(lock_a, lock_b, ready))

    t1.start()
    t2.start()
    ready.set()  # Signal both threads to begin.

    t1.join()
    t2.join()

    print("Part A complete.\n")


# ============================================================================
# PART B: THE FIX — Consistent Lock Ordering
# ============================================================================

def part_b_thread1(lock_a, lock_b, ready_event):
    """Thread 1: acquires locks in GLOBAL ORDER (lock_a, then lock_b)."""
    ready_event.wait()

    print("[Part B - Thread 1] Acquiring lock_a...")
    lock_a.acquire()
    print("[Part B - Thread 1] Holding lock_a. Acquiring lock_b...")

    lock_b.acquire()  # No timeout needed — no deadlock possible.
    print("[Part B - Thread 1] Holding both locks. Doing work...")

    time.sleep(0.3)  # Simulate work while holding both locks.

    lock_b.release()
    lock_a.release()
    print("[Part B - Thread 1] Released both locks. Done.\n")


def part_b_thread2(lock_a, lock_b, ready_event):
    """Thread 2: also acquires locks in GLOBAL ORDER (lock_a, then lock_b)."""
    ready_event.wait()

    print("[Part B - Thread 2] Acquiring lock_a...")
    lock_a.acquire()
    print("[Part B - Thread 2] Holding lock_a. Acquiring lock_b...")

    lock_b.acquire()  # Same order as Thread 1 — no cycle possible.
    print("[Part B - Thread 2] Holding both locks. Doing work...")

    time.sleep(0.3)

    lock_b.release()
    lock_a.release()
    print("[Part B - Thread 2] Released both locks. Done.\n")


def run_part_b():
    """Demonstrate safe execution via consistent lock ordering."""
    print("=" * 60)
    print("PART B: FIX DEMO (Consistent Lock Ordering)")
    print("=" * 60)
    print("Thread 1: lock_a -> lock_b")
    print("Thread 2: lock_a -> lock_b")
    print("Same acquisition order prevents circular wait.\n")

    lock_a = threading.Lock()
    lock_b = threading.Lock()

    ready = threading.Event()
    t1 = threading.Thread(target=part_b_thread1, args=(lock_a, lock_b, ready))
    t2 = threading.Thread(target=part_b_thread2, args=(lock_a, lock_b, ready))

    t1.start()
    t2.start()
    ready.set()

    t1.join()
    t2.join()

    print("Part B complete. No deadlock occurred.\n")


def main():
    print("=== Stage 5: Deadlock Detection and Prevention ===\n")

    run_part_a()
    run_part_b()

    print("=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print(
        "Part A showed a deadlock because threads acquired locks in\n"
        "opposite orders, creating a circular wait. The timeout\n"
        "detected the deadlock instead of hanging forever.\n\n"
        "Part B fixed it by enforcing a global lock ordering: both\n"
        "threads always acquire lock_a before lock_b. This breaks\n"
        "the circular wait condition, making deadlock impossible."
    )


if __name__ == "__main__":
    main()
