#define _POSIX_C_SOURCE 200809L

#ifndef MEMORY_SIMULATOR_H
#define MEMORY_SIMULATOR_H

int find_page(int page, int *frames, int num_frames);
int find_free_frame(int *frames, int num_frames);
void print_frames(int *frames, int num_frames);
double hit_ratio(int hits, int total);
double fault_ratio(int faults, int total);

#endif
