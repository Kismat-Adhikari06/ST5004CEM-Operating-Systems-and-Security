#ifndef AUDIT_LOG_H
#define AUDIT_LOG_H

#include <stdbool.h>

#define MAX_LOG_LINE 512
#define AUDIT_LOG_FILE "audit_log.txt"

typedef struct {
    char log_file[256];
} AuditLogger;

void log_init(AuditLogger *logger, const char *log_file);
void log_event(AuditLogger *logger, const char *username, const char *action, const char *target, const char *result);
void print_log(AuditLogger *logger);
void print_failed_attempts(AuditLogger *logger);

#endif
