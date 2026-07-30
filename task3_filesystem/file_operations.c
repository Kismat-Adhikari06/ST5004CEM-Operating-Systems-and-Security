#define _POSIX_C_SOURCE 200809L
#include "file_operations.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

void fm_init(FileManager *fm, const char *vault_dir)
{
    strncpy(fm->vault_dir, vault_dir, sizeof(fm->vault_dir) - 1);
    fm->vault_dir[sizeof(fm->vault_dir) - 1] = '\0';
    mkdir(fm->vault_dir, 0700);
}

bool fm_is_path_safe(const char *filename)
{
    if (!filename || !*filename)
        return false;

    if (filename[0] == '/' || filename[0] == '\\')
        return false;

    if ((filename[0] >= 'A' && filename[0] <= 'Z') ||
        (filename[0] >= 'a' && filename[0] <= 'z')) {
        if (filename[1] == ':')
            return false;
    }

    if (strstr(filename, "..") != NULL)
        return false;

    return true;
}

bool fm_full_path(FileManager *fm, const char *filename, char *out, size_t out_size)
{
    if (!fm_is_path_safe(filename))
        return false;
    int ret = snprintf(out, out_size, "%s/%s", fm->vault_dir, filename);
    return ret >= 0 && (size_t)ret < out_size;
}

bool fm_create(FileManager *fm, const char *filename, const char *content)
{
    char path[512];
    if (!fm_full_path(fm, filename, path, sizeof(path))) {
        printf("  [CREATE] Error: invalid filename.\n");
        return false;
    }

    if (access(path, F_OK) == 0) {
        printf("  [CREATE] Error: '%s' already exists.\n", filename);
        return false;
    }
    FILE *f = fopen(path, "w");
    if (!f) {
        printf("  [CREATE] Error: cannot create '%s'.\n", filename);
        return false;
    }
    if (content)
        fputs(content, f);
    fclose(f);
    printf("  [CREATE] '%s' created successfully.\n", filename);
    return true;
}

char *fm_read(FileManager *fm, const char *filename)
{
    char path[512];
    if (!fm_full_path(fm, filename, path, sizeof(path))) {
        printf("  [READ] Error: invalid filename.\n");
        return NULL;
    }

    FILE *f = fopen(path, "r");
    if (!f) {
        printf("  [READ] Error: '%s' not found.\n", filename);
        return NULL;
    }

    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    rewind(f);

    char *content = malloc((size_t)(len + 1));
    if (!content) {
        fclose(f);
        return NULL;
    }

    size_t n = fread(content, 1, (size_t)len, f);
    content[n] = '\0';
    fclose(f);
    printf("  [READ] '%s' read successfully.\n", filename);
    return content;
}

bool fm_write(FileManager *fm, const char *filename, const char *content)
{
    char path[512];
    if (!fm_full_path(fm, filename, path, sizeof(path))) {
        printf("  [WRITE] Error: invalid filename.\n");
        return false;
    }

    FILE *f = fopen(path, "w");
    if (!f) {
        printf("  [WRITE] Error: '%s' does not exist.\n", filename);
        return false;
    }
    if (content)
        fputs(content, f);
    fclose(f);
    printf("  [WRITE] '%s' updated successfully.\n", filename);
    return true;
}

bool fm_append(FileManager *fm, const char *filename, const char *content)
{
    char path[512];
    if (!fm_full_path(fm, filename, path, sizeof(path))) {
        printf("  [APPEND] Error: invalid filename.\n");
        return false;
    }

    FILE *f = fopen(path, "a");
    if (!f) {
        printf("  [APPEND] Error: '%s' does not exist.\n", filename);
        return false;
    }
    if (content)
        fputs(content, f);
    fclose(f);
    printf("  [APPEND] '%s' updated successfully.\n", filename);
    return true;
}

bool fm_delete(FileManager *fm, const char *filename)
{
    char path[512];
    if (!fm_full_path(fm, filename, path, sizeof(path))) {
        printf("  [DELETE] Error: invalid filename.\n");
        return false;
    }

    if (unlink(path) != 0) {
        printf("  [DELETE] Error: '%s' not found.\n", filename);
        return false;
    }
    printf("  [DELETE] '%s' deleted successfully.\n", filename);
    return true;
}
