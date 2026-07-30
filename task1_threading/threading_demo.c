#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>

typedef struct {
    const char *name;
    int duration;
} ThreadArg;

void *worker(void *arg)
{
    ThreadArg *ta = (ThreadArg *)arg;
    printf("[%s] Starting work...\n", ta->name);
    sleep(ta->duration);
    printf("[%s] Finished work (slept for %ds).\n", ta->name, ta->duration);
    return NULL;
}

int main(void)
{
    printf("=== Threading Demo ===\n\n");

    ThreadArg args[] = {
        {"Thread-A", 2},
        {"Thread-B", 1},
        {"Thread-C", 3},
    };
    int num = sizeof(args) / sizeof(args[0]);
    pthread_t threads[3];

    printf("Creating and starting threads...\n");
    for (int i = 0; i < num; i++)
    {
        if (pthread_create(&threads[i], NULL, worker, &args[i]) != 0)
        {
            perror("pthread_create");
            exit(1);
        }
        printf("  -> %s has been started.\n", args[i].name);
    }

    printf("\nMain thread waiting for all workers to finish (join)...\n");
    for (int i = 0; i < num; i++)
    {
        pthread_join(threads[i], NULL);
        printf("  -> %s has joined.\n", args[i].name);
    }

    printf("\nAll threads completed. Main thread exiting.\n");
    return 0;
}
