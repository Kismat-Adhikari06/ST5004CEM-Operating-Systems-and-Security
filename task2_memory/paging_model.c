#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <errno.h>
#include "memory_simulator.h"

static long get_positive_int(const char *prompt, long default_val)
{
    char input[64];
    printf("%s [%ld]: ", prompt, default_val);
    if (fgets(input, sizeof(input), stdin) == NULL)
        return default_val;

    char *end;
    long val = strtol(input, &end, 10);

    if (end == input || *end != '\n')
        return default_val;
    if (val <= 0)
    {
        printf("Value must be positive. Using default %ld.\n", default_val);
        return default_val;
    }
    return val;
}

int main(void)
{
    printf("=== Paging Model Simulator ===\n\n");

    long page_size = get_positive_int("Enter page size (bytes)", 4096);
    long num_frames = get_positive_int("Enter number of frames", 4);

    int *frames = malloc((size_t)num_frames * sizeof(int));
    if (!frames)
    {
        fprintf(stderr, "Memory allocation failed.\n");
        return 1;
    }
    for (long i = 0; i < num_frames; i++)
        frames[i] = -1;

    printf("\nPage size: %ld bytes\n", page_size);
    printf("Number of frames: %ld\n", num_frames);
    printf("Logical address space size: %ld bytes\n", page_size * num_frames);
    printf("Page offset bits: %ld\n", (long)(__builtin_ctzl((unsigned long)page_size)));

    char addr_input[64];
    printf("\nEnter logical addresses (one per line). Type 'q' to quit.\n");

    while (1)
    {
        printf("> ");
        if (fgets(addr_input, sizeof(addr_input), stdin) == NULL)
            break;

        if (addr_input[0] == 'q' || addr_input[0] == 'Q')
            break;

        char *end;
        errno = 0;
        long addr = strtol(addr_input, &end, 10);
        if (end == addr_input || *end != '\n' || errno != 0)
        {
            printf("Invalid input. Enter an integer address or 'q' to quit.\n");
            continue;
        }
        if (addr < 0)
        {
            printf("Address must be non-negative.\n");
            continue;
        }

        long page_number = addr / page_size;
        long offset = addr % page_size;
        long frame_number = -1;

        for (long i = 0; i < num_frames; i++)
        {
            if (frames[i] == page_number)
            {
                frame_number = i;
                break;
            }
        }

        if (frame_number == -1)
        {
            int free_idx = find_free_frame(frames, (int)num_frames);
            if (free_idx != -1)
            {
                frames[free_idx] = (int)page_number;
                frame_number = free_idx;
            }
        }

        printf("  Address: %ld  ->  Page: %ld, Offset: %ld", addr, page_number, offset);
        if (frame_number != -1)
            printf(", Frame: %ld", frame_number);
        else
            printf(", Frame: N/A (page fault, no free frame)");
        printf("\n");

        printf("  Frame table: ");
        print_frames(frames, (int)num_frames);
        printf("\n");
    }

    free(frames);
    printf("Goodbye.\n");
    return 0;
}
