#define _POSIX_C_SOURCE 200809L
#include "audit_log.h"
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <pthread.h>

static pthread_mutex_t log_mutex = PTHREAD_MUTEX_INITIALIZER;

void log_init(AuditLogger *logger, const char *log_file)
{
    strncpy(logger->log_file, log_file, sizeof(logger->log_file) - 1);
    logger->log_file[sizeof(logger->log_file) - 1] = '\0';

    FILE *f = fopen(log_file, "a");
    if (f) {
        fseek(f, 0, SEEK_END);
        if (ftell(f) == 0)
            fprintf(f, "=== AUDIT LOG ===\n\n");
        fclose(f);
    }
}

void log_event(AuditLogger *logger, const char *username, const char *action,
               const char *target, const char *result)
{
    time_t now = time(NULL);
    struct tm *tm = localtime(&now);
    char timestamp[20];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", tm);

    pthread_mutex_lock(&log_mutex);
    FILE *f = fopen(logger->log_file, "a");
    if (f) {
        fprintf(f, "[%s] User: %-10s | Action: %-20s | Target: %-20s | Result: %s\n",
                timestamp, username, action, target, result);
        fclose(f);
    }
    pthread_mutex_unlock(&log_mutex);
}

void print_log(AuditLogger *logger)
{
    pthread_mutex_lock(&log_mutex);
    FILE *f = fopen(logger->log_file, "r");
    if (!f) {
        pthread_mutex_unlock(&log_mutex);
        return;
    }
    char line[MAX_LOG_LINE];
    while (fgets(line, sizeof(line), f))
        printf("%s", line);
    fclose(f);
    pthread_mutex_unlock(&log_mutex);
}

void print_failed_attempts(AuditLogger *logger)
{
    pthread_mutex_lock(&log_mutex);
    FILE *f = fopen(logger->log_file, "r");
    if (!f) {
        pthread_mutex_unlock(&log_mutex);
        return;
    }
    char line[MAX_LOG_LINE];
    int count = 0;
    while (fgets(line, sizeof(line), f)) {
        if (strstr(line, "Result: failure")) {
            printf("%s", line);
            count++;
        }
    }
    fclose(f);
    if (count == 0)
        printf("  (no failed attempts)\n");
    pthread_mutex_unlock(&log_mutex);
}
