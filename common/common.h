#ifndef COMMON_H
#define COMMON_H

#include <stdbool.h>
#include <stddef.h>

void trim_newline(char *s);
bool is_positive_int(const char *s);
void bytes_to_hex(const unsigned char *bytes, int len, char *hex);
bool hex_to_bytes(const char *hex, unsigned char *bytes, int len);

#endif
