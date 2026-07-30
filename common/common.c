#define _POSIX_C_SOURCE 200809L
#include "common.h"
#include <stdio.h>
#include <string.h>

void trim_newline(char *s)
{
    size_t len = strlen(s);
    while (len > 0 && (s[len - 1] == '\n' || s[len - 1] == '\r'))
        s[--len] = '\0';
}

bool is_positive_int(const char *s)
{
    if (!s || !*s)
        return false;
    for (const char *p = s; *p; p++)
    {
        if (*p < '0' || *p > '9')
            return false;
    }
    return true;
}

void bytes_to_hex(const unsigned char *bytes, int len, char *hex)
{
    for (int i = 0; i < len; i++)
        sprintf(hex + i * 2, "%02x", bytes[i]);
    hex[len * 2] = '\0';
}

bool hex_to_bytes(const char *hex, unsigned char *bytes, int len)
{
    for (int i = 0; i < len; i++)
    {
        unsigned int b;
        if (sscanf(hex + i * 2, "%2x", &b) != 1)
            return false;
        bytes[i] = (unsigned char)b;
    }
    return true;
}
