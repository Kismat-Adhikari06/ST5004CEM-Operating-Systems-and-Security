#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include "memory_simulator.h"

int main(void)
{
    int refs[] = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};
    int num_refs = sizeof(refs) / sizeof(refs[0]);
    int num_frames = 3;

    char input[16];
    printf("Enter number of frames [%d]: ", num_frames);
    if (fgets(input, sizeof(input), stdin))
    {
        char *end;
        long val = strtol(input, &end, 10);
        if (end != input && *end == '\n' && val > 0)
            num_frames = (int)val;
    }

    int *frames = malloc((size_t)num_frames * sizeof(int));
    if (!frames)
    {
        fprintf(stderr, "Allocation failed.\n");
        return 1;
    }
    for (int i = 0; i < num_frames; i++)
        frames[i] = -1;

    int *queue = malloc((size_t)num_frames * sizeof(int));
    if (!queue)
    {
        fprintf(stderr, "Allocation failed.\n");
        free(frames);
        return 1;
    }

    int head = 0;
    int queue_size = 0;

    int hits = 0, faults = 0;

    printf("\n=== FIFO Page Replacement ===\n");
    printf("Frames: %d\n\n", num_frames);

    for (int i = 0; i < num_refs; i++)
    {
        int page = refs[i];
        int idx = find_page(page, frames, num_frames);

        if (idx != -1)
        {
            hits++;
            printf("Ref %2d (page %2d): HIT  ", i + 1, page);
        }
        else
        {
            faults++;
            int free_idx = find_free_frame(frames, num_frames);
            if (free_idx != -1)
            {
                frames[free_idx] = page;
                queue[queue_size++] = page;
            }
            else
            {
                int evict = queue[head];
                int evict_idx = find_page(evict, frames, num_frames);
                frames[evict_idx] = page;
                queue[head] = page;
                head = (head + 1) % num_frames;
            }
            printf("Ref %2d (page %2d): FAULT", i + 1, page);
        }

        printf("  ");
        print_frames(frames, num_frames);
    }

    printf("\n--- Summary ---\n");
    printf("Total references: %d\n", num_refs);
    printf("Hits:             %d\n", hits);
    printf("Faults:           %d\n", faults);
    printf("Hit ratio:        %.4f\n", hit_ratio(hits, num_refs));
    printf("Fault ratio:      %.4f\n", fault_ratio(faults, num_refs));

    free(frames);
    free(queue);
    return 0;
}
