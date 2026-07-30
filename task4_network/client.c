#define _POSIX_C_SOURCE 200809L

#include "protocol.h"

#include <arpa/inet.h>
#include <ctype.h>
#include <errno.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define DEFAULT_HOST "127.0.0.1"
#define DEFAULT_PORT "5000"
#define MAX_LINE 65536

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

static void build_command(struct json_builder *jb, const char *cmd, const char *data)
{
    json_append(jb, "{\"command\":");
    json_append_escaped(jb, cmd);
    if (data) {
        json_append(jb, ",\"data\":");
        json_append_escaped(jb, data);
    }
    json_append(jb, "}");
}

static void build_login(struct json_builder *jb, const char *user, const char *pass)
{
    json_append(jb, "{\"command\":\"LOGIN\",\"username\":");
    json_append_escaped(jb, user);
    json_append(jb, ",\"password\":");
    json_append_escaped(jb, pass);
    json_append(jb, "}");
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

static int send_request(int sockfd, const char *request, uint32_t req_len)
{
    if (send_frame(sockfd, request, req_len) < 0) {
        fprintf(stderr, "send error: %s\n", strerror(errno));
        return -1;
    }
    return 0;
}

static int print_response(int sockfd)
{
    void *frame = NULL;
    uint32_t flen = 0;
    int r = recv_frame(sockfd, &frame, &flen);
    if (r < 0) {
        fprintf(stderr, "recv error: %s\n", strerror(errno));
        return -1;
    }
    if (r > 0) {
        printf("connection closed by server\n");
        return 1;
    }
    char status[32] = "";
    char result[MAX_LINE] = "";
    char err[MAX_LINE] = "";
    json_find_string(frame, "status", status, sizeof(status));
    json_find_string(frame, "result", result, sizeof(result));
    json_find_string(frame, "error", err, sizeof(err));
    if (strcmp(status, "ok") == 0) {
        printf("OK: %s\n", result);
    } else {
        printf("ERROR: %s\n", err);
    }
    free(frame);
    return 0;
}

static void trim_newline(char *s)
{
    size_t len = strlen(s);
    while (len > 0 && (s[len - 1] == '\n' || s[len - 1] == '\r')) {
        s[--len] = '\0';
    }
}

int main(int argc, char **argv)
{
    const char *host = DEFAULT_HOST;
    const char *port = DEFAULT_PORT;
    const char *cli_user = NULL;
    const char *cli_pass = NULL;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0 && i + 1 < argc) host = argv[++i];
        else if (strcmp(argv[i], "-p") == 0 && i + 1 < argc) port = argv[++i];
        else if (strcmp(argv[i], "-u") == 0 && i + 1 < argc) cli_user = argv[++i];
        else if (strcmp(argv[i], "-P") == 0 && i + 1 < argc) cli_pass = argv[++i];
        else if (strcmp(argv[i], "--help") == 0) {
            printf("Usage: %s [-h host] [-p port] [-u username] [-P password]\n", argv[0]);
            return 0;
        }
    }

    struct addrinfo hints, *res;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    int gai = getaddrinfo(host, port, &hints, &res);
    if (gai != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(gai));
        return 1;
    }

    int sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (sockfd < 0) {
        perror("socket");
        freeaddrinfo(res);
        return 1;
    }

    printf("connecting to %s:%s...\n", host, port);
    if (connect(sockfd, res->ai_addr, res->ai_addrlen) < 0) {
        perror("connect");
        close(sockfd);
        freeaddrinfo(res);
        return 1;
    }
    freeaddrinfo(res);
    printf("connected.\n");

    char username[256] = "";
    char password[256] = "";

    if (cli_user && cli_pass) {
        strncpy(username, cli_user, sizeof(username) - 1);
        strncpy(password, cli_pass, sizeof(password) - 1);
    } else {
        printf("username: ");
        if (!fgets(username, sizeof(username), stdin)) {
            close(sockfd);
            return 1;
        }
        trim_newline(username);

        printf("password: ");
        if (!fgets(password, sizeof(password), stdin)) {
            close(sockfd);
            return 1;
        }
        trim_newline(password);
    }

    {
        struct json_builder req;
        json_init(&req);
        build_login(&req, username, password);
        if (send_request(sockfd, req.buf, (uint32_t)req.len) < 0) {
            json_free(&req);
            close(sockfd);
            return 1;
        }
        json_free(&req);

        void *frame = NULL;
        uint32_t flen = 0;
        int r = recv_frame(sockfd, &frame, &flen);
        if (r < 0) {
            fprintf(stderr, "recv error: %s\n", strerror(errno));
            close(sockfd);
            return 1;
        }
        if (r > 0) {
            printf("server closed connection during login\n");
            close(sockfd);
            return 1;
        }
        char status[32] = "";
        char result[256] = "";
        json_find_string(frame, "status", status, sizeof(status));
        json_find_string(frame, "result", result, sizeof(result));
        if (strcmp(status, "ok") == 0) {
            printf("login: %s\n", result);
        } else {
            char err[256] = "";
            json_find_string(frame, "error", err, sizeof(err));
            printf("login failed: %s\n", err);
            free(frame);
            close(sockfd);
            return 1;
        }
        free(frame);
    }

    printf("\ntype commands: LOGIN, ECHO <text>, UPPERCASE <text>, REVERSE <text>, QUIT\n");

    char line[MAX_LINE];
    while (1) {
        printf("> ");
        fflush(stdout);
        if (!fgets(line, sizeof(line), stdin)) break;
        trim_newline(line);
        if (line[0] == '\0') continue;

        char *space = strchr(line, ' ');
        const char *cmd;
        const char *data = NULL;
        if (space) {
            *space = '\0';
            cmd = line;
            data = space + 1;
            while (*data == ' ') data++;
            if (*data == '\0') data = NULL;
        } else {
            cmd = line;
        }

        struct json_builder req;
        json_init(&req);
        build_command(&req, cmd, data);

        if (send_request(sockfd, req.buf, (uint32_t)req.len) < 0) {
            json_free(&req);
            break;
        }
        json_free(&req);

        int r = print_response(sockfd);
        if (r != 0) break;

        if (strcmp(cmd, "QUIT") == 0) break;
    }

    close(sockfd);
    printf("disconnected.\n");
    return 0;
}
