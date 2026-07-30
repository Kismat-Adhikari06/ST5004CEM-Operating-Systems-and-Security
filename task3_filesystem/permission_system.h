#ifndef PERMISSION_SYSTEM_H
#define PERMISSION_SYSTEM_H

#include <stdbool.h>

#define MAX_PERM_FILES 256
#define PERM_STRING_LEN 9

typedef struct {
    char filename[256];
    char owner[64];
    char permissions[PERM_STRING_LEN + 1];
} PermissionRecord;

typedef struct {
    PermissionRecord records[MAX_PERM_FILES];
    int count;
} PermissionSystem;

void perm_init(PermissionSystem *ps);
bool perm_set(PermissionSystem *ps, const char *filename, const char *owner, const char *perms);
const PermissionRecord *perm_get(PermissionSystem *ps, const char *filename);
bool perm_check(PermissionSystem *ps, const char *filename, const char *username, const char *user_role, const char *action);

#endif
