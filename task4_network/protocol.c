#define _POSIX_C_SOURCE 200809L

#include "protocol.h"

#include <arpa/inet.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

ssize_t send_all(int sockfd, const void *data, size_t len)
{
    const unsigned char *ptr = (const unsigned char *)data;
    size_t remaining = len;

    while (remaining > 0) {
        ssize_t n = send(sockfd, ptr, remaining, MSG_NOSIGNAL);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (n == 0) break;
        ptr += n;
        remaining -= (size_t)n;
    }
    return (ssize_t)(len - remaining);
}

ssize_t recv_all(int sockfd, void *buf, size_t len)
{
    unsigned char *ptr = (unsigned char *)buf;
    size_t remaining = len;

    while (remaining > 0) {
        ssize_t n = recv(sockfd, ptr, remaining, 0);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (n == 0) break;
        ptr += n;
        remaining -= (size_t)n;
    }
    return (ssize_t)(len - remaining);
}

int send_frame(int sockfd, const void *data, uint32_t len)
{
    if (len > MAX_MESSAGE_SIZE) {
        errno = EMSGSIZE;
        return -1;
    }

    uint32_t nlen = htonl(len);
    if (send_all(sockfd, &nlen, sizeof(nlen)) < 0) return -1;
    if (len > 0 && send_all(sockfd, data, len) < 0) return -1;
    return 0;
}

int recv_frame(int sockfd, void **out_data, uint32_t *out_len)
{
    uint32_t nlen = 0;
    ssize_t n = recv_all(sockfd, &nlen, sizeof(nlen));
    if (n < 0) return -1;
    if ((size_t)n < sizeof(nlen)) {
        if (n == 0) {
            *out_data = NULL;
            *out_len = 0;
            return 1;
        }
        errno = ECONNRESET;
        return -1;
    }

    uint32_t len = ntohl(nlen);
    if (len > MAX_MESSAGE_SIZE) {
        errno = EMSGSIZE;
        return -1;
    }

    if (len == 0) {
        *out_data = NULL;
        *out_len = 0;
        return 0;
    }

    void *buf = malloc(len + 1);
    if (!buf) return -1;

    n = recv_all(sockfd, buf, len);
    if (n < 0) {
        free(buf);
        return -1;
    }
    if ((size_t)n < len) {
        free(buf);
        errno = ECONNRESET;
        return -1;
    }

    ((unsigned char *)buf)[len] = '\0';
    *out_data = buf;
    *out_len = len;
    return 0;
}
