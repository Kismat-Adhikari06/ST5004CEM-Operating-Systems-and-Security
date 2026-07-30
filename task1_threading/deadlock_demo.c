#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

pthread_mutex_t lock_a = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t lock_b = PTHREAD_MUTEX_INITIALIZER;

typedef struct {
    pthread_mutex_t *first;
    pthread_mutex_t *second;
    const char *label;
    int part;
} LockArg;

void *thread_deadlock(void *arg)
{
    LockArg *la = (LockArg *)arg;
    printf("[%s] Acquiring first lock...\n", la->label);
    pthread_mutex_lock(la->first);
    printf("[%s] Holding first lock. Sleeping briefly...\n", la->label);
    sleep(1);
    printf("[%s] Trying to acquire second lock...\n", la->label);
    if (pthread_mutex_trylock(la->second) != 0)
        printf("[%s] Could not acquire second lock. Deadlock detected!\n", la->label);
    else
    {
        printf("[%s] Acquired second lock. No deadlock.\n", la->label);
        pthread_mutex_unlock(la->second);
    }
    pthread_mutex_unlock(la->first);
    printf("[%s] Released first lock. Exiting.\n\n", la->label);
    return NULL;
}

void *thread_fixed(void *arg)
{
    LockArg *la = (LockArg *)arg;
    printf("[%s] Acquiring locks in global order...\n", la->label);
    pthread_mutex_lock(la->first);
    pthread_mutex_lock(la->second);
    printf("[%s] Holding both locks. Doing work...\n", la->label);
    sleep(1);
    pthread_mutex_unlock(la->second);
    pthread_mutex_unlock(la->first);
    printf("[%s] Released both locks. Done.\n\n", la->label);
    return NULL;
}

void run_part_a(void)
{
    printf("============================================================\n");
    printf("PART A: DEADLOCK DEMO (Circular Wait)\n");
    printf("============================================================\n");
    printf("Thread 1: lock_a -> sleep -> lock_b\n");
    printf("Thread 2: lock_b -> sleep -> lock_a\n");
    printf("Opposite acquisition order creates a circular wait.\n\n");

    LockArg arg1 = {&lock_a, &lock_b, "Thread 1", 1};
    LockArg arg2 = {&lock_b, &lock_a, "Thread 2", 1};
    pthread_t t1, t2;
    pthread_create(&t1, NULL, thread_deadlock, &arg1);
    pthread_create(&t2, NULL, thread_deadlock, &arg2);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("Part A complete.\n\n");
}

void run_part_b(void)
{
    printf("============================================================\n");
    printf("PART B: FIX DEMO (Consistent Lock Ordering)\n");
    printf("============================================================\n");
    printf("Thread 1: lock_a -> lock_b\n");
    printf("Thread 2: lock_a -> lock_b\n");
    printf("Same acquisition order prevents circular wait.\n\n");

    LockArg arg1 = {&lock_a, &lock_b, "Thread 1", 2};
    LockArg arg2 = {&lock_a, &lock_b, "Thread 2", 2};
    pthread_t t1, t2;
    pthread_create(&t1, NULL, thread_fixed, &arg1);
    pthread_create(&t2, NULL, thread_fixed, &arg2);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("Part B complete. No deadlock occurred.\n\n");
}

int main(void)
{
    printf("=== Deadlock Detection and Prevention ===\n\n");
    run_part_a();
    run_part_b();

    printf("============================================================\n");
    printf("CONCLUSION\n");
    printf("============================================================\n");
    printf("Part A showed a deadlock because threads acquired locks in\n"
           "opposite orders, creating a circular wait.\n\n"
           "Part B fixed it by enforcing a global lock ordering: both\n"
           "threads always acquire lock_a before lock_b. This breaks\n"
           "the circular wait condition, making deadlock impossible.\n");
    return 0;
}
