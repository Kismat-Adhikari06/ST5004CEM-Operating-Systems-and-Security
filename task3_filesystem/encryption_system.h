#ifndef ENCRYPTION_SYSTEM_H
#define ENCRYPTION_SYSTEM_H

#include <stdbool.h>
#include <stddef.h>

#define AES_KEY_SIZE 32
#define AES_IV_SIZE 12
#define AES_TAG_SIZE 16
#define AES_SALT_SIZE 16
#define AES_ITER_COUNT 100000

bool enc_file(const char *vault_dir, const char *filename);
bool dec_file(const char *vault_dir, const char *enc_filename);

#endif
