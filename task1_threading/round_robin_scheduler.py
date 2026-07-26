"""
ST5004CEM - Task 1: Multi-threading
Stage 4: Round-Robin CPU Scheduler Simulation

This script simulates (not controls) a round-robin scheduler — a
classic CPU scheduling algorithm where each process gets a fixed
time slice (quantum) before being preempted and moved to the back
of the ready queue.
"""

from collections import deque


class Process:
    """Represents a process with an ID, name, and burst time."""

    def __init__(self, pid, name, burst_time):
        self.pid = pid
        self.name = name
        self.burst_time = burst_time      # total work needed (time units)
        self.remaining_time = burst_time  # work left after each quantum
        self.completion_time = 0          # when the process finished
        self.waiting_time = 0             # total time spent waiting


def simulate_round_robin(processes, quantum):
    """
    Simulate round-robin scheduling on a list of processes.

    Round-Robin (RR) works like this:
        1. All processes start in a ready queue (FIFO order).
        2. The scheduler takes the first process from the queue.
        3. It lets that process run for at most `quantum` time units.
        4. If the process finishes within the quantum, it is removed
           (completed). If not, it is preempted — the scheduler stops
           it and moves it to the BACK of the queue.
        5. Repeat until all processes are done.

    Why round-robin prevents starvation:
        In algorithms like FCFS (First-Come-First-Served), a process
        with a huge burst time can block the entire queue — a problem
        called the "convoy effect" or starvation. RR fixes this by
        capping how long any single process can hold the CPU. Every
        process gets fair, periodic access regardless of burst time.

    Args:
        processes: list of Process objects.
        quantum: maximum time units a process can run before preemption.

    Returns:
        The processes list with completion_time and waiting_time filled in.
    """
    ready_queue = deque(processes)
    current_time = 0
    completed = []

    print(f"Time Quantum: {quantum} time units")
    print(f"Processes: {[(p.name, p.burst_time) for p in processes]}\n")

    round_num = 0

    while ready_queue:
        round_num += 1
        process = ready_queue.popleft()

        # Determine how long this process will run this turn.
        # It's the minimum of the quantum and whatever time is left.
        run_time = min(quantum, process.remaining_time)

        print(f"Round {round_num}: {process.name} runs for {run_time} units", end="")

        # Simulate the process running — advance the clock.
        current_time += run_time
        process.remaining_time -= run_time

        if process.remaining_time == 0:
            # Process finished — record its completion time.
            process.completion_time = current_time
            process.waiting_time = current_time - process.burst_time
            completed.append(process)
            print(f"  -> COMPLETED")
        else:
            # Not done yet — put it back at the end of the queue.
            ready_queue.append(process)
            print(f"  -> {process.remaining_time} units remaining (back of queue)")

    return completed


def print_summary(completed):
    """Print completion order and average waiting time."""
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    print(f"\n{'Process':<12} {'Burst':<8} {'Completed':<10} {'Waiting':<10}")
    print("-" * 40)

    total_waiting = 0
    for p in completed:
        print(f"{p.name:<12} {p.burst_time:<8} {p.completion_time:<10} {p.waiting_time:<10}")
        total_waiting += p.waiting_time

    avg_waiting = total_waiting / len(completed)
    print("-" * 40)
    print(f"Average waiting time: {avg_waiting:.2f} time units")


def main():
    print("=== Stage 4: Round-Robin CPU Scheduler Simulation ===\n")

    # Define 5 fake processes with varying burst times.
    processes = [
        Process(1, "P1", 6),
        Process(2, "P2", 4),
        Process(3, "P3", 8),
        Process(4, "P4", 3),
        Process(5, "P5", 5),
    ]

    quantum = 2  # Each process gets at most 2 time units per turn.

    completed = simulate_round_robin(processes, quantum)
    print_summary(completed)


if __name__ == "__main__":
    main()
