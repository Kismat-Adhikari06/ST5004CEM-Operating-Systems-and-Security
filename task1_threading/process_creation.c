#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>

int main(void)
{
    pid_t parent_pid = getpid();
    printf("=== Process Creation Demo ===\n\n");
    printf("Parent process PID: %d\n\n", parent_pid);

    pid_t pids[3];

    for (int i = 0; i < 3; i++)
    {
        pids[i] = fork();

        if (pids[i] < 0)
        {
            perror("fork failed");
            exit(1);
        }

        if (pids[i] == 0)
        {
            printf("[Child %d] I am alive! PID=%d, My parent PID=%d\n",
                   i + 1, getpid(), getppid());

            int sum = 0;
            for (int j = 1; j <= 100; j++)
                sum += j;
            printf("[Child %d] Computed sum(1..100) = %d\n", i + 1, sum);

            sleep(1);
            printf("[Child %d] My work is done. Exiting.\n", i + 1);
            exit(0);
        }
        else
        {
            printf("[Parent] Forked child %d (PID=%d)\n", i + 1, pids[i]);
        }
    }

    printf("\n[Parent] Waiting for all children to finish...\n");

    int status;
    pid_t done_pid;
    while ((done_pid = wait(&status)) > 0)
    {
        printf("[Parent] Child PID=%d reaped (exit status: %d)\n",
               done_pid, WEXITSTATUS(status));
    }

    printf("\n[Parent] All children completed. No zombie processes.\n");
    return 0;
}
