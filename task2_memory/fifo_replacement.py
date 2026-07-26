"""
ST5004CEM - Task 2: Memory Management
Stage 2: FIFO Page Replacement

This script extends the paging model from Stage 1 by adding
First-In-First-Out (FIFO) page replacement when memory is full.
"""

from collections import deque


# --- What is FIFO Page Replacement? ---
#
# When a page fault occurs and all frames are full, the OS must evict
# (remove) a page to make room. FIFO evicts the page that has been
# in memory the longest — the "oldest" page by insertion order.
#
# Think of it like a queue at a shop: the first person to arrive is
# the first to leave. Similarly, the first page loaded is the first
# to be evicted when space is needed.
#
# Known weakness of FIFO:
#   FIFO doesn't consider how often or how recently a page is used.
#   A heavily-used page (accessed every few requests) could be evicted
#   simply because it was loaded early, causing a "thrashing" effect
#   where it gets evicted and immediately needed again. This is known
#   as Belady's Anomaly — adding more frames can actually increase
#   page faults with FIFO in some cases.


def simulate_fifo(page_requests, num_frames):
    """
    Simulate paging with FIFO page replacement.

    Uses a queue to track insertion order. When eviction is needed,
    the page at the front of the queue (oldest) is removed.

    Args:
        page_requests: list of page numbers requested.
        num_frames: number of physical frames available.

    Returns:
        (hits, misses) tuple.
    """
    frames = [None] * num_frames

    # The queue tracks insertion order — front is the oldest page.
    # When a page is loaded, its page number is added to the back.
    # When eviction is needed, the front of the queue is removed.
    insertion_order = deque()

    hits = 0
    misses = 0

    print(f"Physical memory: {num_frames} frames")
    print(f"Page requests:   {page_requests}\n")

    for i, page in enumerate(page_requests):
        print(f"Request {i + 1}: Page {page}", end="  |  ")

        if page in frames:
            # HIT — page is already in memory, no action needed.
            hits += 1
            print(f"HIT (page {page} in frame {frames.index(page)})")
        else:
            # MISS — page fault, need to load the page.
            misses += 1

            # Check if there's a free frame.
            free_frame = None
            for j, frame in enumerate(frames):
                if frame is None:
                    free_frame = j
                    break

            if free_frame is not None:
                # Free frame available — load directly, no eviction.
                frames[free_frame] = page
                insertion_order.append(page)
                print(f"MISS -> loaded page {page} into frame {free_frame} (free frame available)")
            else:
                # All frames full — FIFO eviction needed.
                evicted_page = insertion_order.popleft()  # Remove oldest.
                evicted_frame = frames.index(evicted_page)
                frames[evicted_frame] = page
                insertion_order.append(page)
                print(f"MISS -> evicted page {evicted_page} (oldest), loaded page {page} into frame {evicted_frame}")

        print_state(frames)

    return hits, misses


def print_state(frames):
    """Print the current state of all frames."""
    frame_str = "  ".join(
        f"[{f}]" if f is not None else "[ ]" for f in frames
    )
    print(f"  Frames: {frame_str}\n")


def main():
    print("=== Stage 2: FIFO Page Replacement ===\n")

    num_frames = 3

    # Same request sequence as Stage 1 for easy comparison.
    page_requests = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]

    hits, misses = simulate_fifo(page_requests, num_frames)
    total = hits + misses
    hit_ratio = hits / total if total > 0 else 0

    print("=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Total requests: {total}")
    print(f"Hits:           {hits}")
    print(f"Misses:         {misses}")
    print(f"Hit ratio:      {hit_ratio:.4f}")
    print()
    print("FIFO evicts the oldest page regardless of how often it's used.")
    print("Compare with Stage 1 (no replacement) and Stage 3 (LRU).")


if __name__ == "__main__":
    main()
