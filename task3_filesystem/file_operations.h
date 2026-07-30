#ifndef FILE_OPERATIONS_H
#define FILE_OPERATIONS_H

#include <stdbool.h>
#include <stddef.h>

#define MAX_FILENAME 256
#define VAULT_DIR "vault"

typedef struct {
    char vault_dir[256];
} FileManager;

void fm_init(FileManager *fm, const char *vault_dir);
bool fm_is_path_safe(const char *filename);
bool fm_full_path(FileManager *fm, const char *filename, char *out, size_t out_size);
bool fm_create(FileManager *fm, const char *filename, const char *content);
char *fm_read(FileManager *fm, const char *filename);
bool fm_write(FileManager *fm, const char *filename, const char *content);
bool fm_append(FileManager *fm, const char *filename, const char *content);
bool fm_delete(FileManager *fm, const char *filename);

#endif
