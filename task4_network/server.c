#define _POSIX_C_SOURCE 200809L

#include "protocol.h"

#include <arpa/inet.h>
#include <ctype.h>
#include <errno.h>
#include <openssl/sha.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define PORT 5000
#define BACKLOG 16
#define CLIENT_TIMEOUT 60
#define MAX_USERNAME 64
#define MAX_PASSWORD 128
#define HASH_HEX_SIZE (SHA256_DIGEST_LENGTH * 2 + 1)

struct user {
    char username[MAX_USERNAME];
    char pass_hash[HASH_HEX_SIZE];
};

static struct user users[] = {
    {"alice",   "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"},
    {"bob",     "62380bf91b37c27a23d587ff63134079b0cae1a184eac32176574be179dba1bb"},
    {"charlie", "22ad18a03fd26627225366c2337f1c93693c89fc89b62b8dff3d393e9761d139"},
};
static const int num_users = sizeof(users) / sizeof(users[0]);

static volatile int server_running = 1;
static int server_fd = -1;

static void hex_encode(const unsigned char *in, size_t in_len, char *out)
{
    static const char hex[] = "0123456789abcdef";
    for (size_t i = 0; i < in_len; i++) {
        out[i * 2]     = hex[(in[i] >> 4) & 0xf];
        out[i * 2 + 1] = hex[in[i] & 0xf];
    }
    out[in_len * 2] = '\0';
}

static void hash_password(const char *password, char *hex_out)
{
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256((const unsigned char *)password, strlen(password), hash);
    hex_encode(hash, SHA256_DIGEST_LENGTH, hex_out);
}

static const char *json_find_string(const char *json, const char *key, char *out, size_t out_size)
{
    if (!json || !key || !out) return NULL;
    size_t klen = strlen(key);
    const char *p = json;
    while ((p = strstr(p, key)) != NULL) {
        const char *before = p - 1;
        if (before >= json && !(*before == '"' || *before == ' ' || *before == '{' || *before == ',' || *before == ':')) {
            p++;
            continue;
        }
        p += klen;
        while (*p && (*p == ' ' || *p == ':')) p++;
        if (*p != '"') continue;
        p++;
        const char *start = p;
        while (*p && *p != '"') p++;
        if (!*p) return NULL;
        size_t len = (size_t)(p - start);
        if (len >= out_size) len = out_size - 1;
        memcpy(out, start, len);
        out[len] = '\0';
        return p + 1;
    }
    return NULL;
}

struct json_builder {
    char *buf;
    size_t cap;
    size_t len;
};

static void json_init(struct json_builder *jb)
{
    jb->buf = NULL;
    jb->cap = 0;
    jb->len = 0;
}

static void json_append(struct json_builder *jb, const char *s)
{
    size_t slen = strlen(s);
    if (jb->len + slen + 1 > jb->cap) {
        size_t newcap = jb->cap ? jb->cap * 2 : 256;
        while (jb->len + slen + 1 > newcap) newcap *= 2;
        char *tmp = realloc(jb->buf, newcap);
        if (!tmp) return;
        jb->buf = tmp;
        jb->cap = newcap;
    }
    memcpy(jb->buf + jb->len, s, slen);
    jb->len += slen;
    jb->buf[jb->len] = '\0';
}

static void json_append_escaped(struct json_builder *jb, const char *s)
{
    json_append(jb, "\"");
    while (*s) {
        switch (*s) {
        case '"':  json_append(jb, "\\\""); break;
        case '\\': json_append(jb, "\\\\"); break;
        case '\n': json_append(jb, "\\n");  break;
        case '\r': json_append(jb, "\\r");  break;
        case '\t': json_append(jb, "\\t");  break;
        default:
            if ((unsigned char)*s < 0x20) {
                char esc[8];
                snprintf(esc, sizeof(esc), "\\u%04x", (unsigned char)*s);
                json_append(jb, esc);
            } else {
                char c[2] = {*s, '\0'};
                json_append(jb, c);
            }
            break;
        }
        s++;
    }
    json_append(jb, "\"");
}

static void json_free(struct json_builder *jb)
{
    free(jb->buf);
    jb->buf = NULL;
}

static void build_response(struct json_builder *jb,
                           const char *status,
                           const char *result_field,
                           const char *result_val)
{
    json_append(jb, "{\"status\":");
    json_append_escaped(jb, status);
    if (result_field && result_val) {
        json_append(jb, ",");
        json_append_escaped(jb, result_field);
        json_append(jb, ":");
        json_append_escaped(jb, result_val);
    }
    json_append(jb, "}");
}

static void build_login_ok(struct json_builder *jb, const char *username)
{
    json_append(jb, "{");
    json_append(jb, "\"status\":\"ok\",");
    json_append(jb, "\"result\":\"Login successful\",");
    json_append(jb, "\"authenticated\":true,");
    json_append(jb, "\"username\":");
    json_append_escaped(jb, username);
    json_append(jb, "}");
}

static int authenticate(const char *username, const char *password)
{
    char hash[HASH_HEX_SIZE];
    hash_password(password, hash);
    for (int i = 0; i < num_users; i++) {
        if (strcmp(users[i].username, username) == 0 &&
            strcmp(users[i].pass_hash, hash) == 0) {
            return 1;
        }
    }
    return 0;
}

static void *handle_client(void *arg)
{
    int client_fd = *(int *)arg;
    free(arg);

    struct sockaddr_in peer;
    socklen_t peer_len = sizeof(peer);
    char peer_str[64] = "unknown";
    if (getpeername(client_fd, (struct sockaddr *)&peer, &peer_len) == 0) {
        inet_ntop(AF_INET, &peer.sin_addr, peer_str, sizeof(peer_str));
    }

    printf("[server] connection from %s\n", peer_str);

    struct timeval tv;
    tv.tv_sec = CLIENT_TIMEOUT;
    tv.tv_usec = 0;
    setsockopt(client_fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    int authenticated = 0;
    char username[MAX_USERNAME] = "";

    while (1) {
        void *frame = NULL;
        uint32_t flen = 0;
        int r = recv_frame(client_fd, &frame, &flen);
        if (r < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK)
                printf("[server] %s timed out\n", peer_str);
            else
                printf("[server] %s recv error: %s\n", peer_str, strerror(errno));
            break;
        }
        if (r > 0) {
            printf("[server] %s disconnected\n", peer_str);
            break;
        }

        struct json_builder resp;
        json_init(&resp);

        char cmd[64] = "";
        char data_val[MAX_MESSAGE_SIZE] = "";
        char user_val[MAX_USERNAME] = "";
        char pass_val[MAX_PASSWORD] = "";

        json_find_string(frame, "command", cmd, sizeof(cmd));

        if (strcmp(cmd, "LOGIN") == 0) {
            json_find_string(frame, "username", user_val, sizeof(user_val));
            json_find_string(frame, "password", pass_val, sizeof(pass_val));

            if (user_val[0] == '\0' || pass_val[0] == '\0') {
                build_response(&resp, "error", "error",
                    "LOGIN requires 'username' and 'password' fields");
            } else if (authenticate(user_val, pass_val)) {
                authenticated = 1;
                strncpy(username, user_val, MAX_USERNAME - 1);
                username[MAX_USERNAME - 1] = '\0';
                build_login_ok(&resp, username);
            } else {
                build_response(&resp, "error", "error", "Invalid credentials");
            }
        } else if (!authenticated) {
            build_response(&resp, "error", "error",
                "Not authenticated. Please LOGIN first.");
        } else if (strcmp(cmd, "QUIT") == 0) {
            build_response(&resp, "ok", "result", "Goodbye");
            if (send_frame(client_fd, resp.buf, (uint32_t)resp.len) < 0) {
                printf("[server] %s send error: %s\n", peer_str, strerror(errno));
            }
            json_free(&resp);
            free(frame);
            break;
        } else if (strcmp(cmd, "ECHO") == 0) {
            json_find_string(frame, "data", data_val, sizeof(data_val));
            build_response(&resp, "ok", "result", data_val);
        } else if (strcmp(cmd, "UPPERCASE") == 0) {
            json_find_string(frame, "data", data_val, sizeof(data_val));
            for (char *p = data_val; *p; p++) *p = (char)toupper((unsigned char)*p);
            build_response(&resp, "ok", "result", data_val);
        } else if (strcmp(cmd, "REVERSE") == 0) {
            json_find_string(frame, "data", data_val, sizeof(data_val));
            size_t dlen = strlen(data_val);
            for (size_t i = 0; i < dlen / 2; i++) {
                char t = data_val[i];
                data_val[i] = data_val[dlen - 1 - i];
                data_val[dlen - 1 - i] = t;
            }
            build_response(&resp, "ok", "result", data_val);
        } else {
            char errmsg[128];
            snprintf(errmsg, sizeof(errmsg), "Unknown command: '%s'", cmd);
            build_response(&resp, "error", "error", errmsg);
        }

        if (resp.buf) {
            if (send_frame(client_fd, resp.buf, (uint32_t)resp.len) < 0) {
                printf("[server] %s send error: %s\n", peer_str, strerror(errno));
            }
            json_free(&resp);
        }

        free(frame);
    }

    close(client_fd);
    printf("[server] %s connection closed\n", peer_str);
    return NULL;
}

static void sigint_handler(int sig)
{
    (void)sig;
    server_running = 0;
    if (server_fd >= 0) {
        close(server_fd);
        server_fd = -1;
    }
}

int main(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = sigint_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    signal(SIGPIPE, SIG_IGN);

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return 1;
    }

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        close(server_fd);
        return 1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(server_fd);
        return 1;
    }

    if (listen(server_fd, BACKLOG) < 0) {
        perror("listen");
        close(server_fd);
        return 1;
    }

    printf("[server] listening on port %d\n", PORT);

    while (server_running) {
        struct sockaddr_in peer;
        socklen_t peer_len = sizeof(peer);
        int *client_fd = malloc(sizeof(int));
        if (!client_fd) break;

        *client_fd = accept(server_fd, (struct sockaddr *)&peer, &peer_len);
        if (*client_fd < 0) {
            free(client_fd);
            if (!server_running) break;
            if (errno == EINTR) continue;
            perror("accept");
            continue;
        }

        pthread_t tid;
        pthread_attr_t attr;
        pthread_attr_init(&attr);
        pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
        if (pthread_create(&tid, &attr, handle_client, client_fd) != 0) {
            perror("pthread_create");
            close(*client_fd);
            free(client_fd);
        }
        pthread_attr_destroy(&attr);
    }

    if (server_fd >= 0) {
        close(server_fd);
    }
    printf("[server] shut down\n");
    return 0;
}
