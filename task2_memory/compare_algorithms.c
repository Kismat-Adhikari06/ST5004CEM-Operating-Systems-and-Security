#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include "memory_simulator.h"

typedef struct
{
    int *frames;
    int *last_used;
    int head;
    int queue_size;
    int hits;
    int faults;
} SimState;

static void reset_frames(int *frames, int n)
{
    for (int i = 0; i < n; i++)
        frames[i] = -1;
}

static void run_fifo(const int *refs, int num_refs, int num_frames,
                     int *hits, int *faults)
{
    int *frames = malloc((size_t)num_frames * sizeof(int));
    int *queue = malloc((size_t)num_frames * sizeof(int));
    reset_frames(frames, num_frames);

    int head = 0, qsize = 0;
    *hits = 0;
    *faults = 0;

    for (int i = 0; i < num_refs; i++)
    {
        int page = refs[i];
        if (find_page(page, frames, num_frames) != -1)
        {
            (*hits)++;
        }
        else
        {
            (*faults)++;
            int free_idx = find_free_frame(frames, num_frames);
            if (free_idx != -1)
            {
                frames[free_idx] = page;
                queue[qsize++] = page;
            }
            else
            {
                int evict = queue[head];
                int evict_idx = find_page(evict, frames, num_frames);
                frames[evict_idx] = page;
                queue[head] = page;
                head = (head + 1) % num_frames;
            }
        }
    }

    free(frames);
    free(queue);
}

static void run_lru(const int *refs, int num_refs, int num_frames,
                    int *hits, int *faults)
{
    int *frames = malloc((size_t)num_frames * sizeof(int));
    int *last_used = malloc((size_t)num_frames * sizeof(int));
    reset_frames(frames, num_frames);
    for (int i = 0; i < num_frames; i++)
        last_used[i] = -1;

    *hits = 0;
    *faults = 0;

    for (int i = 0; i < num_refs; i++)
    {
        int page = refs[i];
        int idx = find_page(page, frames, num_frames);
        if (idx != -1)
        {
            (*hits)++;
            last_used[idx] = i;
        }
        else
        {
            (*faults)++;
            int free_idx = find_free_frame(frames, num_frames);
            if (free_idx != -1)
            {
                frames[free_idx] = page;
                last_used[free_idx] = i;
            }
            else
            {
                int lru_idx = 0;
                for (int j = 1; j < num_frames; j++)
                    if (last_used[j] < last_used[lru_idx])
                        lru_idx = j;
                frames[lru_idx] = page;
                last_used[lru_idx] = i;
            }
        }
    }

    free(frames);
    free(last_used);
}

static void print_separator(void)
{
    printf("+-------------+--------+-------+------+--------+-----------+-----------+\n");
}

static void run_both(const int *refs, int num_refs, int num_frames)
{
    int fifo_hits, fifo_faults, lru_hits, lru_faults;

    run_fifo(refs, num_refs, num_frames, &fifo_hits, &fifo_faults);
    run_lru(refs, num_refs, num_frames, &lru_hits, &lru_faults);

    printf("| %-11s | %6d | %5d | %4d | %6d | %9.4f | %9.4f |\n",
           "FIFO", num_frames, num_refs, fifo_hits, fifo_faults,
           hit_ratio(fifo_hits, num_refs), fault_ratio(fifo_faults, num_refs));
    printf("| %-11s | %6d | %5d | %4d | %6d | %9.4f | %9.4f |\n",
           "LRU", num_frames, num_refs, lru_hits, lru_faults,
           hit_ratio(lru_hits, num_refs), fault_ratio(lru_faults, num_refs));
    print_separator();
}

int main(void)
{
    int seq1[] = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};
    int seq2[] = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};
    int seq3[] = {1, 2, 1, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5, 1, 2, 3, 6, 1, 2, 3};
    int n1 = sizeof(seq1) / sizeof(seq1[0]);
    int n2 = sizeof(seq2) / sizeof(seq2[0]);
    int n3 = sizeof(seq3) / sizeof(seq3[0]);

    printf("=== Algorithm Comparison: FIFO vs LRU ===\n\n");

    print_separator();
    printf("| %-11s | %-6s | %-5s | %-4s | %-6s | %-9s | %-9s |\n",
           "Algorithm", "Frames", "Total", "Hits", "Faults", "Hit Ratio", "Fault Ratio");
    print_separator();

    run_both(seq1, n1, 3);
    run_both(seq2, n2, 4);
    run_both(seq3, n3, 3);

    return 0;
}
