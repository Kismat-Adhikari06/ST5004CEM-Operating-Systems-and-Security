#ifndef AUTH_SYSTEM_H
#define AUTH_SYSTEM_H

#include <stdbool.h>

#define MAX_USERNAME 64
#define MAX_PASSWORD 128
#define MAX_STORED_USERS 128
#define SALT_SIZE 16
#define HASH_SIZE 32
#define ITER_COUNT 100000

typedef struct {
    char username[MAX_USERNAME];
    char salt_hex[SALT_SIZE * 2 + 1];
    char hash_hex[HASH_SIZE * 2 + 1];
    char role[16];
    int iteration_count;
} StoredUser;

typedef struct {
    StoredUser users[MAX_STORED_USERS];
    int count;
    char current_user[MAX_USERNAME];
    bool logged_in;
} AuthSystem;

void auth_init(AuthSystem *auth);
bool auth_register(AuthSystem *auth, const char *username, const char *password, const char *role);
bool auth_login(AuthSystem *auth, const char *username, const char *password);
void auth_logout(AuthSystem *auth);
bool auth_is_logged_in(AuthSystem *auth);
const char *auth_get_current_user(AuthSystem *auth);
const char *auth_get_user_role(AuthSystem *auth);

#endif
