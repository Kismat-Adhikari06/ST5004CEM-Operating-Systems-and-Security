"""
ST5004CEM - Task 1: Multi-threading
Stage 2: Demonstrating a Race Condition

This script deliberately creates a race condition on a shared variable
to show why synchronization is needed. No locks are used — that's Stage 3.
"""

import threading
import time

# Shared global counter — all threads will read and write this variable.
# In Python, global variables are shared across all threads in the same
# process, which is exactly what makes this race condition possible.
counter = 0


def increment(thread_name, iterations):
    """
    Increment the shared counter multiple times.

    Each increment is a THREE-step operation:
        1. READ  the current value of counter into a local variable
        2. MODIFY the local variable (+1)
        3. WRITE the local variable back to counter

    This is called a "read-modify-write" sequence. The race condition
    happens because another thread can execute its own read-modify-write
    between steps 1 and 3 of this thread's sequence.

    Example of the bug:
        Thread-A reads counter = 5
        Thread-B reads counter = 5        (counter hasn't changed yet!)
        Thread-A writes counter = 6       (5 + 1)
        Thread-B writes counter = 6       (5 + 1, NOT 6 + 1!)
        Expected: counter = 7, Actual: counter = 6
        One increment is silently lost.
    """
    global counter

    for _ in range(iterations):
        # Step 1: READ — grab the current value of the shared counter.
        temp = counter

        # This tiny sleep deliberately widens the race window.
        # It gives the OS thread scheduler a chance to switch to
        # another thread right between the read and the write.
        # Without this sleep, the race still exists but is much
        # harder to observe because it happens so fast.
        time.sleep(0.0001)

        # Step 3: WRITE — put the incremented value back.
        # But if another thread read counter BEFORE this write,
        # its copy is now stale, and its write will overwrite
        # ours (or vice versa), losing an increment.
        counter = temp + 1


def main():
    global counter
    counter = 0  # Reset for a clean run.

    print("=== Stage 2: Race Condition Demo ===\n")

    iterations_per_thread = 1000
    num_threads = 3
    expected = iterations_per_thread * num_threads

    print(f"Shared counter starts at: {counter}")
    print(f"Each of {num_threads} threads will increment {iterations_per_thread} times")
    print(f"Expected final value: {expected}\n")

    # Create and start 3 threads — all targeting the same increment()
    # function, all writing to the same global counter.
    threads = []
    for i in range(num_threads):
        t = threading.Thread(
            target=increment,
            args=(f"Thread-{i+1}", iterations_per_thread),
        )
        threads.append(t)
        t.start()

    # Wait for all threads to finish before reading the final value.
    for t in threads:
        t.join()

    # Show the result — it should be LESS than 3000 due to lost increments.
    print(f"Expected value: {expected}")
    print(f"Actual value:   {counter}")
    print(f"Lost increments: {expected - counter}")

    if counter < expected:
        print(
            "\nThe counter is wrong because threadsinterleaved their"
            "\nread-modify-write operations. Each lost increment means"
            "\ntwo threads read the same value before either wrote back."
        )
    else:
        print(
            "\nBy luck, no increments were lost this time. Run again —"
            "\nthe result will likely differ because thread scheduling"
            "\nis non-deterministic."
        )


if __name__ == "__main__":
    main()
