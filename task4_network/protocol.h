#ifndef PROTOCOL_H
#define PROTOCOL_H

#define _POSIX_C_SOURCE 200809L

#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>

#define MAX_MESSAGE_SIZE 65536

ssize_t send_all(int sockfd, const void *data, size_t len);
ssize_t recv_all(int sockfd, void *buf, size_t len);
int send_frame(int sockfd, const void *data, uint32_t len);
int recv_frame(int sockfd, void **out_data, uint32_t *out_len);

#endif
