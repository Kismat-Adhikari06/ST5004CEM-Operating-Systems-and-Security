#define _POSIX_C_SOURCE 200809L
#include "auth_system.h"
#include <string.h>
#include <stdio.h>
#include <openssl/evp.h>
#include <openssl/rand.h>

static void bytes_to_hex(const unsigned char *bytes, int len, char *hex)
{
    for (int i = 0; i < len; i++)
        sprintf(hex + i * 2, "%02x", bytes[i]);
    hex[len * 2] = '\0';
}

static bool hex_to_bytes(const char *hex, unsigned char *bytes, int len)
{
    for (int i = 0; i < len; i++) {
        unsigned int b;
        if (sscanf(hex + i * 2, "%2x", &b) != 1)
            return false;
        bytes[i] = (unsigned char)b;
    }
    return true;
}

void auth_init(AuthSystem *auth)
{
    auth->count = 0;
    auth->logged_in = false;
    auth->current_user[0] = '\0';
}

bool auth_register(AuthSystem *auth, const char *username, const char *password, const char *role)
{
    for (int i = 0; i < auth->count; i++) {
        if (strcmp(auth->users[i].username, username) == 0) {
            printf("  [REGISTER] Error: username '%s' already taken.\n", username);
            return false;
        }
    }
    if (auth->count >= MAX_STORED_USERS) {
        printf("  [REGISTER] Error: user limit reached.\n");
        return false;
    }

    unsigned char salt[SALT_SIZE];
    unsigned char hash[HASH_SIZE];
    if (RAND_bytes(salt, SALT_SIZE) != 1) {
        printf("  [REGISTER] Error: failed to generate salt.\n");
        return false;
    }

    if (PKCS5_PBKDF2_HMAC(password, (int)strlen(password), salt, SALT_SIZE,
                          ITER_COUNT, EVP_sha256(), HASH_SIZE, hash) != 1) {
        printf("  [REGISTER] Error: key derivation failed.\n");
        return false;
    }

    StoredUser *u = &auth->users[auth->count++];
    strncpy(u->username, username, MAX_USERNAME - 1);
    u->username[MAX_USERNAME - 1] = '\0';
    strncpy(u->role, role, sizeof(u->role) - 1);
    u->role[sizeof(u->role) - 1] = '\0';
    bytes_to_hex(salt, SALT_SIZE, u->salt_hex);
    bytes_to_hex(hash, HASH_SIZE, u->hash_hex);
    u->iteration_count = ITER_COUNT;

    printf("  [REGISTER] User '%s' registered successfully (role: %s).\n", username, role);
    return true;
}

bool auth_login(AuthSystem *auth, const char *username, const char *password)
{
    StoredUser *found = NULL;
    for (int i = 0; i < auth->count; i++) {
        if (strcmp(auth->users[i].username, username) == 0) {
            found = &auth->users[i];
            break;
        }
    }
    if (!found) {
        printf("  [LOGIN] Invalid credentials.\n");
        return false;
    }

    unsigned char salt[SALT_SIZE];
    unsigned char hash[HASH_SIZE];
    if (!hex_to_bytes(found->salt_hex, salt, SALT_SIZE)) {
        printf("  [LOGIN] Invalid credentials.\n");
        return false;
    }

    if (PKCS5_PBKDF2_HMAC(password, (int)strlen(password), salt, SALT_SIZE,
                          found->iteration_count, EVP_sha256(), HASH_SIZE, hash) != 1) {
        printf("  [LOGIN] Invalid credentials.\n");
        return false;
    }

    char hash_hex[HASH_SIZE * 2 + 1];
    bytes_to_hex(hash, HASH_SIZE, hash_hex);

    if (strcmp(hash_hex, found->hash_hex) != 0) {
        printf("  [LOGIN] Invalid credentials.\n");
        return false;
    }

    auth->logged_in = true;
    strncpy(auth->current_user, username, MAX_USERNAME - 1);
    auth->current_user[MAX_USERNAME - 1] = '\0';
    printf("  [LOGIN] Welcome, %s!\n", username);
    return true;
}

void auth_logout(AuthSystem *auth)
{
    if (auth->logged_in) {
        printf("  [LOGOUT] User '%s' logged out.\n", auth->current_user);
        auth->logged_in = false;
        auth->current_user[0] = '\0';
    } else {
        printf("  [LOGOUT] No user is currently logged in.\n");
    }
}

bool auth_is_logged_in(AuthSystem *auth)
{
    return auth->logged_in;
}

const char *auth_get_current_user(AuthSystem *auth)
{
    if (auth->logged_in)
        return auth->current_user;
    return NULL;
}

const char *auth_get_user_role(AuthSystem *auth)
{
    if (!auth->logged_in)
        return NULL;
    for (int i = 0; i < auth->count; i++) {
        if (strcmp(auth->users[i].username, auth->current_user) == 0)
            return auth->users[i].role;
    }
    return NULL;
}
