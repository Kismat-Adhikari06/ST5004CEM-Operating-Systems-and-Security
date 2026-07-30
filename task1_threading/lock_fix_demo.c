#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define NUM_THREADS 3
#define ITERATIONS  1000
#define EXPECTED    (NUM_THREADS * ITERATIONS)

int counter = 0;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void *increment(void *arg)
{
    (void)arg;
    for (int i = 0; i < ITERATIONS; i++)
    {
        pthread_mutex_lock(&lock);
        int temp = counter;
        volatile int spin = 0;
        while (spin < 10000) spin++;
        counter = temp + 1;
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}

int main(void)
{
    counter = 0;
    printf("=== Lock Fix Demo ===\n\n");
    printf("Shared counter starts at: %d\n", counter);
    printf("Each of %d threads will increment %d times\n", NUM_THREADS, ITERATIONS);
    printf("Expected final value: %d\n", EXPECTED);
    printf("Using pthread_mutex_t to protect the critical section.\n\n");

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

    if (counter == EXPECTED)
        printf("\nThe counter is correct! The lock ensured each\n"
               "read-modify-write completed without interference.\n");
    else
        printf("\nSomething went wrong.\n");

    return 0;
}
