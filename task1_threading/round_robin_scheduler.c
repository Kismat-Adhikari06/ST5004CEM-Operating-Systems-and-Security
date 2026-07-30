#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int pid;
    char name[16];
    int burst_time;
    int remaining_time;
    int completion_time;
    int waiting_time;
} Process;

typedef struct {
    Process **items;
    int head;
    int tail;
    int size;
    int capacity;
} Queue;

Queue *queue_create(int capacity)
{
    Queue *q = malloc(sizeof(Queue));
    q->items = malloc(capacity * sizeof(Process *));
    q->head = 0;
    q->tail = 0;
    q->size = 0;
    q->capacity = capacity;
    return q;
}

void queue_push(Queue *q, Process *p)
{
    q->items[q->tail] = p;
    q->tail = (q->tail + 1) % q->capacity;
    q->size++;
}

Process *queue_pop(Queue *q)
{
    Process *p = q->items[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->size--;
    return p;
}

int queue_empty(Queue *q)
{
    return q->size == 0;
}

void simulate_round_robin(Process *processes, int num, int quantum)
{
    Queue *q = queue_create(num);
    for (int i = 0; i < num; i++)
        queue_push(q, &processes[i]);

    int current_time = 0;
    int round_num = 0;

    printf("Time Quantum: %d time units\n", quantum);
    printf("Processes: [");
    for (int i = 0; i < num; i++)
    {
        if (i > 0) printf(", ");
        printf("('%s', %d)", processes[i].name, processes[i].burst_time);
    }
    printf("]\n\n");

    while (!queue_empty(q))
    {
        round_num++;
        Process *p = queue_pop(q);
        int run_time = quantum < p->remaining_time ? quantum : p->remaining_time;
        printf("Round %d: %s runs for %d units", round_num, p->name, run_time);
        current_time += run_time;
        p->remaining_time -= run_time;

        if (p->remaining_time == 0)
        {
            p->completion_time = current_time;
            p->waiting_time = current_time - p->burst_time;
            printf("  -> COMPLETED\n");
        }
        else
        {
            queue_push(q, p);
            printf("  -> %d units remaining (back of queue)\n", p->remaining_time);
        }
    }

    printf("\n==================================================\n");
    printf("SUMMARY\n");
    printf("==================================================\n");
    printf("%-12s %-8s %-10s %-10s\n", "Process", "Burst", "Completed", "Waiting");
    printf("----------------------------------------\n");
    int total_waiting = 0;
    for (int i = 0; i < num; i++)
    {
        printf("%-12s %-8d %-10d %-10d\n",
               processes[i].name, processes[i].burst_time,
               processes[i].completion_time, processes[i].waiting_time);
        total_waiting += processes[i].waiting_time;
    }
    printf("----------------------------------------\n");
    printf("Average waiting time: %.2f time units\n", (double)total_waiting / num);

    free(q->items);
    free(q);
}

int main(void)
{
    printf("=== Round-Robin CPU Scheduler Simulation ===\n\n");

    Process processes[5] = {
        {1, "P1", 6, 6, 0, 0},
        {2, "P2", 4, 4, 0, 0},
        {3, "P3", 8, 8, 0, 0},
        {4, "P4", 3, 3, 0, 0},
        {5, "P5", 5, 5, 0, 0},
    };
    int num = 5;
    int quantum = 2;

    simulate_round_robin(processes, num, quantum);
    return 0;
}
