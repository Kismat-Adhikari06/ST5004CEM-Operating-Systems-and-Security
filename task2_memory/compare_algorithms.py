"""
ST5004CEM - Task 2: Memory Management
Stage 4: FIFO vs LRU Comparison Runner

Runs both algorithms on identical inputs and prints live-computed
results side-by-side. All numbers come from the simulation — nothing
is hardcoded.
"""

from collections import deque


# --- Why Algorithm Performance Depends on the Workload ---
#
# There is no universally "best" page replacement algorithm.
# Performance depends on the specific memory access pattern:
#
#   - LRU excels when there's strong "temporal locality" — i.e., pages
#     accessed recently are likely to be accessed again soon. Real
#     programs often exhibit this (loops, repeated function calls).
#
#   - FIFO can perform equally well (or even better) on workloads with
#     uniform access patterns where no page is reused more than others.
#
#   - FIFO suffers from "Belady's Anomaly" — adding more frames can
#     paradoxically increase page faults. LRU does not have this issue.
#
# The best way to choose an algorithm is to test it against realistic
# workloads from your target application. That's exactly what this
# script does — compares algorithms on different configurations.


# ============================================================================
# FIFO Implementation
# ============================================================================

def run_fifo(page_requests, num_frames):
    """
    Run FIFO page replacement and return statistics.

    Returns:
        dict with keys: hits, misses, total, hit_ratio
    """
    frames = [None] * num_frames
    insertion_order = deque()
    hits = 0
    misses = 0

    for page in page_requests:
        if page in frames:
            hits += 1
        else:
            misses += 1
            free_frame = None
            for j, frame in enumerate(frames):
                if frame is None:
                    free_frame = j
                    break

            if free_frame is not None:
                frames[free_frame] = page
                insertion_order.append(page)
            else:
                evicted = insertion_order.popleft()
                evicted_frame = frames.index(evicted)
                frames[evicted_frame] = page
                insertion_order.append(page)

    total = hits + misses
    hit_ratio = hits / total if total > 0 else 0

    return {"hits": hits, "misses": misses, "total": total, "hit_ratio": hit_ratio}


# ============================================================================
# LRU Implementation
# ============================================================================

def run_lru(page_requests, num_frames):
    """
    Run LRU page replacement and return statistics.

    Returns:
        dict with keys: hits, misses, total, hit_ratio
    """
    frames = [None] * num_frames
    last_used = {}
    hits = 0
    misses = 0

    for step, page in enumerate(page_requests):
        if page in frames:
            hits += 1
            last_used[page] = step
        else:
            misses += 1
            free_frame = None
            for j, frame in enumerate(frames):
                if frame is None:
                    free_frame = j
                    break

            if free_frame is not None:
                frames[free_frame] = page
                last_used[page] = step
            else:
                lru_page = min(frames, key=lambda p: last_used[p])
                lru_frame = frames.index(lru_page)
                del last_used[lru_page]
                frames[lru_frame] = page
                last_used[page] = step

    total = hits + misses
    hit_ratio = hits / total if total > 0 else 0

    return {"hits": hits, "misses": misses, "total": total, "hit_ratio": hit_ratio}


# ============================================================================
# Comparison Printing
# ============================================================================

def print_comparison(label, requests, num_frames, fifo_result, lru_result):
    """Print a clean side-by-side comparison table."""
    print(f"\n{'=' * 60}")
    print(f" {label}")
    print(f" Frames: {num_frames}  |  Requests: {len(requests)} pages")
    print(f" Request sequence: {requests}")
    print(f"{'=' * 60}")

    print(f"\n {'Metric':<18} {'FIFO':<12} {'LRU':<12} {'Winner'}")
    print(f" {'-'*18} {'-'*12} {'-'*12} {'-'*10}")

    for metric, key in [("Hits", "hits"), ("Misses", "misses"), ("Hit Ratio", "hit_ratio")]:
        f_val = fifo_result[key]
        l_val = lru_result[key]

        if metric == "Hit Ratio":
            f_str = f"{f_val:.4f}"
            l_str = f"{l_val:.4f}"
        else:
            f_str = str(f_val)
            l_str = str(l_val)

        if key == "misses":
            winner = "FIFO" if f_val < l_val else "LRU" if l_val < f_val else "Tie"
        else:
            winner = "FIFO" if f_val > l_val else "LRU" if l_val > f_val else "Tie"

        print(f" {metric:<18} {f_str:<12} {l_str:<12} {winner}")

    print()


def main():
    print("=== Stage 4: FIFO vs LRU Comparison ===\n")

    # --- Configuration 1: Original workload ---
    requests_1 = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    frames_1 = 3

    fifo_1 = run_fifo(requests_1, frames_1)
    lru_1 = run_lru(requests_1, frames_1)
    print_comparison("Config 1: 3 frames, 12 requests", requests_1, frames_1, fifo_1, lru_1)

    # --- Configuration 2: More frames (4) ---
    requests_2 = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    frames_2 = 4

    fifo_2 = run_fifo(requests_2, frames_2)
    lru_2 = run_lru(requests_2, frames_2)
    print_comparison("Config 2: 4 frames, 12 requests (same sequence)", requests_2, frames_2, fifo_2, lru_2)

    # --- Configuration 3: Longer, different workload ---
    requests_3 = [1, 2, 1, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5, 1, 2, 3, 6, 1, 2, 3]
    frames_3 = 3

    fifo_3 = run_fifo(requests_3, frames_3)
    lru_3 = run_lru(requests_3, frames_3)
    print_comparison("Config 3: 3 frames, 20 requests (longer sequence)", requests_3, frames_3, fifo_3, lru_3)

    # --- Summary ---
    print("=" * 60)
    print(" ANALYSIS")
    print("=" * 60)
    print(
        "Performance depends on the workload's access pattern.\n"
        "LRU generally does better when pages are reused frequently\n"
        "(temporal locality). FIFO can match or beat LRU when access\n"
        "is uniform with no reuse pattern. More frames reduce faults\n"
        "for both algorithms, but the relative benefit of LRU over\n"
        "FIFO varies by workload — there is no single 'best' algorithm."
    )


if __name__ == "__main__":
    main()
