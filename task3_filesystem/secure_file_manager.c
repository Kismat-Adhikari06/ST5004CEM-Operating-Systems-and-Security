#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "auth_system.h"
#include "file_operations.h"
#include "permission_system.h"
#include "encryption_system.h"
#include "audit_log.h"

static AuthSystem auth;
static FileManager fm;
static PermissionSystem ps;
static AuditLogger logger;

static void trim_newline(char *s)
{
    size_t len = strlen(s);
    if (len > 0 && s[len - 1] == '\n')
        s[len - 1] = '\0';
}

static bool require_login(void)
{
    if (!auth_is_logged_in(&auth)) {
        printf("  [ERROR] No user logged in. Please log in first.\n");
        return false;
    }
    return true;
}

static bool check_file_perm(const char *filename, const char *action)
{
    const char *user = auth_get_current_user(&auth);
    const char *role = auth_get_user_role(&auth);
    if (!perm_check(&ps, filename, user, role, action)) {
        printf("  [DENIED] '%s' does not have %s permission on '%s'.\n", user, action, filename);
        log_event(&logger, user, action, filename, "failure");
        return false;
    }
    return true;
}

static void menu_register(void)
{
    char user[MAX_USERNAME], pass[MAX_PASSWORD], role[16];
    printf("  Username: ");
    fgets(user, sizeof(user), stdin); trim_newline(user);
    printf("  Password: ");
    fgets(pass, sizeof(pass), stdin); trim_newline(pass);
    printf("  Role (owner/group/other): ");
    fgets(role, sizeof(role), stdin); trim_newline(role);

    if (auth_register(&auth, user, pass, role)) {
        log_event(&logger, user, "register", "-", "success");
    } else {
        log_event(&logger, user, "register", "-", "failure");
    }
}

static void menu_login(void)
{
    char user[MAX_USERNAME], pass[MAX_PASSWORD];
    printf("  Username: ");
    fgets(user, sizeof(user), stdin); trim_newline(user);
    printf("  Password: ");
    fgets(pass, sizeof(pass), stdin); trim_newline(pass);

    if (auth_login(&auth, user, pass)) {
        log_event(&logger, user, "login", "-", "success");
    } else {
        log_event(&logger, user, "login", "-", "failure");
    }
}

static void menu_logout(void)
{
    const char *user = auth_get_current_user(&auth);
    auth_logout(&auth);
    if (user)
        log_event(&logger, user, "logout", "-", "success");
}

static void menu_create(void)
{
    if (!require_login()) return;
    const char *user = auth_get_current_user(&auth);
    char filename[MAX_FILENAME], content[1024];
    printf("  Filename: ");
    fgets(filename, sizeof(filename), stdin); trim_newline(filename);
    printf("  Content: ");
    fgets(content, sizeof(content), stdin); trim_newline(content);

    if (fm_create(&fm, filename, content)) {
        perm_set(&ps, filename, user, "rw-------");
        log_event(&logger, user, "create", filename, "success");
    } else {
        log_event(&logger, user, "create", filename, "failure");
    }
}

static void menu_read(void)
{
    if (!require_login()) return;
    const char *user = auth_get_current_user(&auth);
    char filename[MAX_FILENAME];
    printf("  Filename: ");
    fgets(filename, sizeof(filename), stdin); trim_newline(filename);

    if (!check_file_perm(filename, "read")) return;

    char *content = fm_read(&fm, filename);
    if (content) {
        printf("  Content:\n%s\n", content);
        free(content);
        log_event(&logger, user, "read", filename, "success");
    } else {
        log_event(&logger, user, "read", filename, "failure");
    }
}

static void menu_write(void)
{
    if (!require_login()) return;
    const char *user = auth_get_current_user(&auth);
    char filename[MAX_FILENAME], content[1024], mode[8];
    printf("  Filename: ");
    fgets(filename, sizeof(filename), stdin); trim_newline(filename);
    printf("  Overwrite or Append? (w/a): ");
    fgets(mode, sizeof(mode), stdin); trim_newline(mode);

    if (!check_file_perm(filename, "write")) return;

    printf("  Content: ");
    fgets(content, sizeof(content), stdin); trim_newline(content);

    bool ok;
    if (mode[0] == 'a' || mode[0] == 'A')
        ok = fm_append(&fm, filename, content);
    else
        ok = fm_write(&fm, filename, content);

    if (ok)
        log_event(&logger, user, "write", filename, "success");
    else
        log_event(&logger, user, "write", filename, "failure");
}

static void menu_delete(void)
{
    if (!require_login()) return;
    const char *user = auth_get_current_user(&auth);
    char filename[MAX_FILENAME];
    printf("  Filename: ");
    fgets(filename, sizeof(filename), stdin); trim_newline(filename);

    if (!check_file_perm(filename, "write")) return;

    if (fm_delete(&fm, filename)) {
        log_event(&logger, user, "delete", filename, "success");
    } else {
        log_event(&logger, user, "delete", filename, "failure");
    }
}

static void menu_view_perms(void)
{
    if (!require_login()) return;
    char filename[MAX_FILENAME];
    printf("  Filename: ");
    fgets(filename, sizeof(filename), stdin); trim_newline(filename);

    const PermissionRecord *r = perm_get(&ps, filename);
    if (r)
        printf("  Owner: %s  Permissions: %s\n", r->owner, r->permissions);
    else
        printf("  No permissions record found for '%s'.\n", filename);
}

static void menu_change_perms(void)
{
    if (!require_login()) return;
    const char *user = auth_get_current_user(&auth);
    char filename[MAX_FILENAME], perms[16], owner[64];
    printf("  Filename: ");
    fgets(filename, sizeof(filename), stdin); trim_newline(filename);
    printf("  New owner: ");
    fgets(owner, sizeof(owner), stdin); trim_newline(owner);
    printf("  Permissions (9 chars, e.g. rw-r-----): ");
    fgets(perms, sizeof(perms), stdin); trim_newline(perms);

    if (perm_set(&ps, filename, owner, perms)) {
        log_event(&logger, user, "chmod", filename, "success");
        printf("  [PERMS] Permissions updated.\n");
    } else {
        log_event(&logger, user, "chmod", filename, "failure");
        printf("  [PERMS] Failed to update permissions.\n");
    }
}

static void menu_encrypt(void)
{
    if (!require_login()) return;
    const char *user = auth_get_current_user(&auth);
    char filename[MAX_FILENAME];
    printf("  Filename to encrypt: ");
    fgets(filename, sizeof(filename), stdin); trim_newline(filename);

    if (!check_file_perm(filename, "read")) return;

    if (enc_file(fm.vault_dir, filename)) {
        log_event(&logger, user, "encrypt", filename, "success");
    } else {
        log_event(&logger, user, "encrypt", filename, "failure");
    }
}

static void menu_decrypt(void)
{
    if (!require_login()) return;
    const char *user = auth_get_current_user(&auth);
    char enc_filename[MAX_FILENAME];
    printf("  .enc filename to decrypt: ");
    fgets(enc_filename, sizeof(enc_filename), stdin); trim_newline(enc_filename);

    size_t len = strlen(enc_filename);
    if (len > 4 && strcmp(enc_filename + len - 4, ".enc") == 0) {
        char orig[MAX_FILENAME];
        memcpy(orig, enc_filename, len - 4);
        orig[len - 4] = '\0';
        if (perm_get(&ps, orig))
            if (!check_file_perm(orig, "write")) return;
    }

    if (dec_file(fm.vault_dir, enc_filename)) {
        log_event(&logger, user, "decrypt", enc_filename, "success");
    } else {
        log_event(&logger, user, "decrypt", enc_filename, "failure");
    }
}

static void menu_audit_log(void)
{
    if (!require_login()) return;
    printf("\n--- Audit Log ---\n");
    print_log(&logger);
}

int main(void)
{
    auth_init(&auth);
    fm_init(&fm, VAULT_DIR);
    perm_init(&ps);
    log_init(&logger, AUDIT_LOG_FILE);

    printf("=== Secure File Manager ===\n");

    int choice;
    do {
        printf("\n"
               "  1. Register\n"
               "  2. Login\n"
               "  3. Logout\n"
               "  4. Create file\n"
               "  5. Read file\n"
               "  6. Write/Append file\n"
               "  7. Delete file\n"
               "  8. View permissions\n"
               "  9. Change permissions\n"
               " 10. Encrypt file\n"
               " 11. Decrypt file\n"
               " 12. View audit log\n"
               " 13. Exit\n"
               "Choice: ");
        char buf[16];
        fgets(buf, sizeof(buf), stdin);
        choice = atoi(buf);

        switch (choice) {
            case 1:  menu_register();    break;
            case 2:  menu_login();       break;
            case 3:  menu_logout();      break;
            case 4:  menu_create();      break;
            case 5:  menu_read();        break;
            case 6:  menu_write();       break;
            case 7:  menu_delete();      break;
            case 8:  menu_view_perms();  break;
            case 9:  menu_change_perms();break;
            case 10: menu_encrypt();     break;
            case 11: menu_decrypt();     break;
            case 12: menu_audit_log();   break;
            case 13: printf("  Exiting.\n"); break;
            default: printf("  Invalid choice.\n"); break;
        }
    } while (choice != 13);

    return 0;
}
