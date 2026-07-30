#include "memory_simulator.h"
#include <stdio.h>

int find_page(int page, int *frames, int num_frames)
{
    for (int i = 0; i < num_frames; i++)
    {
        if (frames[i] == page)
            return i;
    }
    return -1;
}

int find_free_frame(int *frames, int num_frames)
{
    for (int i = 0; i < num_frames; i++)
    {
        if (frames[i] == -1)
            return i;
    }
    return -1;
}

void print_frames(int *frames, int num_frames)
{
    printf("[ ");
    for (int i = 0; i < num_frames; i++)
    {
        if (frames[i] == -1)
            printf(". ");
        else
            printf("%d ", frames[i]);
    }
    printf("]\n");
}

double hit_ratio(int hits, int total)
{
    if (total == 0)
        return 0.0;
    return (double)hits / total;
}

double fault_ratio(int faults, int total)
{
    if (total == 0)
        return 0.0;
    return (double)faults / total;
}
