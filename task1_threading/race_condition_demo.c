#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define NUM_THREADS 3
#define ITERATIONS  1000
#define EXPECTED    (NUM_THREADS * ITERATIONS)

int counter = 0;

void *increment(void *arg)
{
    (void)arg;
    for (int i = 0; i < ITERATIONS; i++)
    {
        int temp = counter;
        volatile int spin = 0;
        while (spin < 10000) spin++;
        counter = temp + 1;
    }
    return NULL;
}

int main(void)
{
    counter = 0;
    printf("=== Race Condition Demo ===\n\n");
    printf("Shared counter starts at: %d\n", counter);
    printf("Each of %d threads will increment %d times\n", NUM_THREADS, ITERATIONS);
    printf("Expected final value: %d\n\n", EXPECTED);

    pthread_t threads[NUM_THREADS];
    for (int i = 0; i < NUM_THREADS; i++)
    {
        if (pthread_create(&threads[i], NULL, increment, NULL) != 0)
        {
            perror("pthread_create");
            exit(1);
        }
    }

    for (int i = 0; i < NUM_THREADS; i++)
        pthread_join(threads[i], NULL);

    printf("Expected value: %d\n", EXPECTED);
    printf("Actual value:   %d\n", counter);
    printf("Lost increments: %d\n", EXPECTED - counter);

    if (counter < EXPECTED)
        printf("\nThe counter is wrong because threads interleaved their\n"
               "read-modify-write operations.\n");
    else
        printf("\nBy luck, no increments were lost this time.\n");

    return 0;
}
