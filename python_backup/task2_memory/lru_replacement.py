"""
ST5004CEM - Task 2: Memory Management
Stage 3: LRU Page Replacement

This script implements Least Recently Used (LRU) page replacement
and uses the same inputs as FIFO for direct comparison.
"""


# --- FIFO vs LRU: What's the Difference? ---
#
# FIFO:  Evicts the page that was loaded EARLIEST (insertion order).
#        It doesn't care if a page is accessed constantly — if it was
#        loaded first, it goes first.
#
# LRU:   Evicts the page that was used LEAST RECENTLY (access order).
#        A page loaded long ago but accessed a moment ago is kept.
#        A page loaded recently but never accessed again is evicted.
#
# Why LRU generally performs better:
#   Real programs exhibit "temporal locality" — data that was accessed
#   recently is likely to be accessed again soon (e.g., loop variables,
#   frequently called functions). LRU exploits this by keeping recently-
#   used pages in memory, which aligns with real workload patterns.
#
#   FIFO ignores usage entirely, so it may evict a hot (frequently used)
#   page just because it was loaded early, causing an immediate fault.
#
# Cost of LRU:  Tracking "last used" time requires extra bookkeeping
#               per access, whereas FIFO only tracks insertion order.


def simulate_lru(page_requests, num_frames):
    """
    Simulate paging with LRU page replacement.

    Tracks the last access time for each page in memory. When eviction
    is needed, the page with the oldest last-access time is removed.

    Args:
        page_requests: list of page numbers requested.
        num_frames: number of physical frames available.

    Returns:
        (hits, misses) tuple.
    """
    frames = [None] * num_frames

    # Maps each loaded page to its last access time (step number).
    # When a page is accessed (hit or initial load), its timestamp
    # is updated. On eviction, the page with the smallest timestamp
    # (least recently used) is chosen.
    last_used = {}

    hits = 0
    misses = 0

    print(f"Physical memory: {num_frames} frames")
    print(f"Page requests:   {page_requests}\n")

    for step, page in enumerate(page_requests):
        print(f"Request {step + 1}: Page {page}", end="  |  ")

        if page in frames:
            # HIT — page is in memory. Update its last-used time.
            hits += 1
            last_used[page] = step
            print(f"HIT (page {page} in frame {frames.index(page)})")
        else:
            # MISS — page fault, need to load the page.
            misses += 1

            # Check for a free frame first.
            free_frame = None
            for j, frame in enumerate(frames):
                if frame is None:
                    free_frame = j
                    break

            if free_frame is not None:
                # Free frame available — load directly.
                frames[free_frame] = page
                last_used[page] = step
                print(f"MISS -> loaded page {page} into frame {free_frame} (free frame available)")
            else:
                # All frames full — LRU eviction needed.
                # Find the page with the smallest last-used time.
                lru_page = min(frames, key=lambda p: last_used[p])
                lru_frame = frames.index(lru_page)
                del last_used[lru_page]
                frames[lru_frame] = page
                last_used[page] = step
                print(f"MISS -> evicted page {lru_page} (least recently used), loaded page {page} into frame {lru_frame}")

        print_state(frames)

    return hits, misses


def print_state(frames):
    """Print the current state of all frames."""
    frame_str = "  ".join(
        f"[{f}]" if f is not None else "[ ]" for f in frames
    )
    print(f"  Frames: {frame_str}\n")


def main():
    print("=== Stage 3: LRU Page Replacement ===\n")

    num_frames = 3

    # Exact same sequence as FIFO for fair comparison.
    page_requests = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]

    hits, misses = simulate_lru(page_requests, num_frames)
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
    print("Comparison:")
    print("  Stage 1 (No replacement): 0 hits, 12 misses")
    print("  Stage 2 (FIFO):           2 hits, 10 misses")
    print(f"  Stage 3 (LRU):            {hits} hits, {misses} misses")
    print()
    print("LRU performs better because it keeps frequently used pages")
    print("in memory, exploiting temporal locality in the workload.")


if __name__ == "__main__":
    main()
