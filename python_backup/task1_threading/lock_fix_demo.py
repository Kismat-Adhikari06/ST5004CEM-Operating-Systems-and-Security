"""
ST5004CEM - Task 1: Multi-threading
Stage 3: Fixing the Race Condition with a Lock (Mutex)

This script fixes the race condition from Stage 2 by protecting the
shared counter with a threading.Lock, ensuring mutual exclusion.
"""

import threading
import time

counter = 0

# A lock (mutex) ensures only one thread can hold it at a time.
# When a thread acquires the lock, all other threads trying to
# acquire it will block (wait) until the holder releases it.
lock = threading.Lock()


def increment(thread_name, iterations):
    """
    Increment the shared counter safely using a lock.

    The "critical section" is the code that accesses shared state:
        temp = counter       # READ
        time.sleep(...)      # simulate work
        counter = temp + 1   # WRITE

    Without a lock, two threads can both READ the same stale value
    before either writes back, losing an increment (Stage 2).

    With "with lock:", only ONE thread can execute the critical
    section at a time. While it holds the lock, all other threads
    are blocked waiting. This makes the read-modify-write sequence
    "atomic" relative to other threads — no interleaving can occur.
    """
    global counter

    for _ in range(iterations):
        # "with lock:" acquires the lock, and automatically releases
        # it when the block ends (even if an exception occurs).
        # While one thread is inside this block, all others wait
        # at this same line until the lock is free.
        with lock:
            # --- Critical Section Start ---
            # Only one thread executes these lines at any given time.
            temp = counter
            time.sleep(0.0001)  # Same delay as Stage 2, but now safe.
            counter = temp + 1
            # --- Critical Section End ---


def main():
    global counter
    counter = 0

    print("=== Stage 3: Lock Fix Demo ===\n")

    iterations_per_thread = 1000
    num_threads = 3
    expected = iterations_per_thread * num_threads

    print(f"Shared counter starts at: {counter}")
    print(f"Each of {num_threads} threads will increment {iterations_per_thread} times")
    print(f"Expected final value: {expected}")
    print("Using threading.Lock to protect the critical section.\n")

    threads = []
    start_time = time.time()

    for i in range(num_threads):
        t = threading.Thread(
            target=increment,
            args=(f"Thread-{i+1}", iterations_per_thread),
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.time() - start_time

    print(f"Expected value: {expected}")
    print(f"Actual value:   {counter}")
    print(f"Time elapsed:   {elapsed:.2f}s")

    if counter == expected:
        print(
            "\nThe counter is correct! The lock ensured each"
            "\nread-modify-write completed without interference"
            "\nfrom other threads."
        )
    else:
        print(
            "\nSomething went wrong — the counter is incorrect."
            "\nCheck the lock implementation."
        )


if __name__ == "__main__":
    main()
