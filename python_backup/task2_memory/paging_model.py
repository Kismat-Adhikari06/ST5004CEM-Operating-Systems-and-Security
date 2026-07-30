"""
ST5004CEM - Task 2: Memory Management
Stage 1: Basic Paging Model (Skeleton)

This script simulates a paging system with page frames and page requests.
Replacement algorithms (FIFO, LRU) will be added in later stages.
"""


# --- What is Paging? ---
#
# In real operating systems, memory is divided into fixed-size blocks:
#   - "Pages"  = fixed-size blocks of virtual/logical memory (what a process sees)
#   - "Frames" = fixed-size blocks of physical memory (actual RAM)
#
# The OS keeps a "page table" mapping each page to the frame it occupies.
# When a process accesses a page that isn't loaded in any frame, a
# "page fault" occurs — the OS must load that page from disk into a
# free frame (or evict another page to make room).
#
# This script simulates that process in a simplified way.


def simulate_paging(page_requests, num_frames):
    """
    Simulate paging with hit/miss tracking.

    Args:
        page_requests: list of page numbers the "process" is requesting.
        num_frames: how many physical frames are available.

    Returns:
        (hits, misses) tuple after processing all requests.
    """
    # Physical memory is represented as a list of frames.
    # Each frame either holds a page number or is None (empty).
    frames = [None] * num_frames

    hits = 0
    misses = 0

    print(f"Physical memory: {num_frames} frames")
    print(f"Page requests:   {page_requests}\n")

    for i, page in enumerate(page_requests):
        print(f"Request {i + 1}: Page {page}", end="  |  ")

        # Check if the page is already in memory (a "hit").
        if page in frames:
            hits += 1
            print(f"HIT (page {page} is in frame {frames.index(page)})")
        else:
            # Page fault (a "miss") — page is not in memory.
            misses += 1

            # Find a free (empty) frame.
            free_frame = None
            for j, frame in enumerate(frames):
                if frame is None:
                    free_frame = j
                    break

            if free_frame is not None:
                # There's space — load the page into the free frame.
                frames[free_frame] = page
                print(f"MISS -> loaded page {page} into frame {free_frame}")
            else:
                # All frames are occupied — replacement is needed.
                # This is where FIFO/LRU will go in Stage 2 and 3.
                print(f"MISS -> page {page} needs to be loaded but ALL FRAMES FULL (eviction needed here)")

        print_state(frames)

    return hits, misses


def print_state(frames):
    """Print the current state of all frames."""
    frame_str = "  ".join(
        f"[{f}]" if f is not None else "[ ]" for f in frames
    )
    print(f"  Frames: {frame_str}\n")


def main():
    print("=== Stage 1: Basic Paging Model ===\n")

    num_frames = 3

    # A sequence of page requests — simulates a program accessing pages.
    # Expected behavior with 3 frames and no eviction:
    #   Pages 1, 2, 3 fill the frames (3 misses, 0 hits).
    #   Pages 4 triggers "eviction needed" (all frames full).
    #   Remaining requests also trigger "eviction needed".
    page_requests = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]

    hits, misses = simulate_paging(page_requests, num_frames)
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
    print("Note: This stage does NOT handle eviction. Requests after")
    print("all frames are full just print a placeholder message.")
    print("Stage 2 (FIFO) and Stage 3 (LRU) will add replacement logic.")


if __name__ == "__main__":
    main()
