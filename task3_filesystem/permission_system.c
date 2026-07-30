#define _POSIX_C_SOURCE 200809L
#include "permission_system.h"
#include <stdio.h>
#include <string.h>

void perm_init(PermissionSystem *ps)
{
    ps->count = 0;
}

bool perm_set(PermissionSystem *ps, const char *filename, const char *owner, const char *perms)
{
    for (int i = 0; i < ps->count; i++) {
        if (strcmp(ps->records[i].filename, filename) == 0) {
            strncpy(ps->records[i].owner, owner, sizeof(ps->records[i].owner) - 1);
            strncpy(ps->records[i].permissions, perms, PERM_STRING_LEN);
            ps->records[i].permissions[PERM_STRING_LEN] = '\0';
            return true;
        }
    }
    if (ps->count >= MAX_PERM_FILES)
        return false;

    PermissionRecord *r = &ps->records[ps->count++];
    strncpy(r->filename, filename, sizeof(r->filename) - 1);
    r->filename[sizeof(r->filename) - 1] = '\0';
    strncpy(r->owner, owner, sizeof(r->owner) - 1);
    r->owner[sizeof(r->owner) - 1] = '\0';
    strncpy(r->permissions, perms, PERM_STRING_LEN);
    r->permissions[PERM_STRING_LEN] = '\0';
    return true;
}

const PermissionRecord *perm_get(PermissionSystem *ps, const char *filename)
{
    for (int i = 0; i < ps->count; i++) {
        if (strcmp(ps->records[i].filename, filename) == 0)
            return &ps->records[i];
    }
    return NULL;
}

bool perm_check(PermissionSystem *ps, const char *filename,
                const char *username, const char *user_role, const char *action)
{
    const PermissionRecord *r = perm_get(ps, filename);
    if (!r)
        return false;

    const char *segment;
    if (strcmp(username, r->owner) == 0)
        segment = r->permissions;
    else if (strcmp(user_role, "group") == 0)
        segment = r->permissions + 3;
    else
        segment = r->permissions + 6;

    char required;
    if (strcmp(action, "read") == 0)
        required = 'r';
    else if (strcmp(action, "write") == 0)
        required = 'w';
    else if (strcmp(action, "execute") == 0)
        required = 'x';
    else
        return false;

    return strchr(segment, required) != NULL;
}
