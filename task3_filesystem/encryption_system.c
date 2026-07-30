#define _POSIX_C_SOURCE 200809L
#include "encryption_system.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
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

bool enc_file(const char *vault_dir, const char *filename)
{
    char path[512];
    snprintf(path, sizeof(path), "%s/%s", vault_dir, filename);

    FILE *fin = fopen(path, "rb");
    if (!fin) {
        printf("  [ENCRYPT] Error: cannot open '%s'.\n", filename);
        return false;
    }
    fseek(fin, 0, SEEK_END);
    long plain_len = ftell(fin);
    rewind(fin);

    unsigned char *plaintext = malloc((size_t)plain_len + 1);
    if (!plaintext) { fclose(fin); return false; }
    fread(plaintext, 1, (size_t)plain_len, fin);
    plaintext[plain_len] = '\0';
    fclose(fin);

    unsigned char key_seed[AES_KEY_SIZE];
    unsigned char salt[AES_SALT_SIZE];
    unsigned char iv[AES_IV_SIZE];
    unsigned char aes_key[AES_KEY_SIZE];
    unsigned char tag[AES_TAG_SIZE];

    if (RAND_bytes(key_seed, AES_KEY_SIZE) != 1 ||
        RAND_bytes(salt, AES_SALT_SIZE) != 1 ||
        RAND_bytes(iv, AES_IV_SIZE) != 1) {
        printf("  [ENCRYPT] Error: random generation failed.\n");
        free(plaintext);
        return false;
    }

    if (PKCS5_PBKDF2_HMAC((const char *)key_seed, AES_KEY_SIZE,
                          salt, AES_SALT_SIZE, AES_ITER_COUNT,
                          EVP_sha256(), AES_KEY_SIZE, aes_key) != 1) {
        printf("  [ENCRYPT] Error: key derivation failed.\n");
        free(plaintext);
        return false;
    }

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) { free(plaintext); return false; }

    int len;
    unsigned char *ciphertext = malloc((size_t)plain_len + AES_TAG_SIZE);
    if (!ciphertext) { EVP_CIPHER_CTX_free(ctx); free(plaintext); return false; }

    EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, AES_IV_SIZE, NULL);
    EVP_EncryptInit_ex(ctx, NULL, NULL, aes_key, iv);
    EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, (int)plain_len);
    int cipher_len = len;
    EVP_EncryptFinal_ex(ctx, ciphertext + cipher_len, &len);
    cipher_len += len;
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, AES_TAG_SIZE, tag);
    EVP_CIPHER_CTX_free(ctx);

    char enc_path[520];
    snprintf(enc_path, sizeof(enc_path), "%s.enc", path);
    FILE *fout = fopen(enc_path, "wb");
    if (!fout) {
        printf("  [ENCRYPT] Error: cannot create .enc file.\n");
        free(ciphertext); free(plaintext);
        return false;
    }
    fwrite(salt, 1, AES_SALT_SIZE, fout);
    fwrite(iv, 1, AES_IV_SIZE, fout);
    fwrite(tag, 1, AES_TAG_SIZE, fout);
    fwrite(ciphertext, 1, (size_t)cipher_len, fout);
    fclose(fout);

    char key_path[520];
    snprintf(key_path, sizeof(key_path), "%s.enc.key", path);
    FILE *fkey = fopen(key_path, "w");
    if (!fkey) {
        printf("  [ENCRYPT] Error: cannot create .key file.\n");
        free(ciphertext); free(plaintext);
        return false;
    }
    char hex[AES_KEY_SIZE * 2 + 1];
    bytes_to_hex(key_seed, AES_KEY_SIZE, hex);
    fprintf(fkey, "%s\n", hex);
    fclose(fkey);

    free(ciphertext);
    free(plaintext);
    printf("  [ENCRYPT] '%s' -> '%s.enc'\n", filename, filename);
    return true;
}

bool dec_file(const char *vault_dir, const char *enc_filename)
{
    char enc_path[512];
    snprintf(enc_path, sizeof(enc_path), "%s/%s", vault_dir, enc_filename);

    FILE *fenc = fopen(enc_path, "rb");
    if (!fenc) {
        printf("  [DECRYPT] Error: cannot open '%s'.\n", enc_filename);
        return false;
    }

    unsigned char salt[AES_SALT_SIZE];
    unsigned char iv[AES_IV_SIZE];
    unsigned char tag[AES_TAG_SIZE];

    if (fread(salt, 1, AES_SALT_SIZE, fenc) != AES_SALT_SIZE ||
        fread(iv, 1, AES_IV_SIZE, fenc) != AES_IV_SIZE ||
        fread(tag, 1, AES_TAG_SIZE, fenc) != AES_TAG_SIZE) {
        printf("  [DECRYPT] Error: invalid .enc file format.\n");
        fclose(fenc);
        return false;
    }

    fseek(fenc, 0, SEEK_END);
    long total = ftell(fenc);
    long cipher_len = total - (long)(AES_SALT_SIZE + AES_IV_SIZE + AES_TAG_SIZE);
    rewind(fenc);
    fseek(fenc, AES_SALT_SIZE + AES_IV_SIZE + AES_TAG_SIZE, SEEK_SET);

    unsigned char *ciphertext = malloc((size_t)cipher_len);
    if (!ciphertext) { fclose(fenc); return false; }
    fread(ciphertext, 1, (size_t)cipher_len, fenc);
    fclose(fenc);

    char key_path[520];
    snprintf(key_path, sizeof(key_path), "%s.key", enc_path);
    FILE *fkey = fopen(key_path, "r");
    if (!fkey) {
        printf("  [DECRYPT] Error: key file not found.\n");
        free(ciphertext);
        return false;
    }
    char hex[AES_KEY_SIZE * 2 + 2];
    if (!fgets(hex, sizeof(hex), fkey)) {
        fclose(fkey); free(ciphertext);
        printf("  [DECRYPT] Error: cannot read key file.\n");
        return false;
    }
    fclose(fkey);
    size_t hex_len = strlen(hex);
    if (hex_len > 0 && hex[hex_len - 1] == '\n')
        hex[hex_len - 1] = '\0';

    unsigned char key_seed[AES_KEY_SIZE];
    if (!hex_to_bytes(hex, key_seed, AES_KEY_SIZE)) {
        printf("  [DECRYPT] Error: invalid key format.\n");
        free(ciphertext);
        return false;
    }

    unsigned char aes_key[AES_KEY_SIZE];
    if (PKCS5_PBKDF2_HMAC((const char *)key_seed, AES_KEY_SIZE,
                          salt, AES_SALT_SIZE, AES_ITER_COUNT,
                          EVP_sha256(), AES_KEY_SIZE, aes_key) != 1) {
        printf("  [DECRYPT] Error: key derivation failed.\n");
        free(ciphertext);
        return false;
    }

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) { free(ciphertext); return false; }

    int len;
    unsigned char *plaintext = malloc((size_t)cipher_len + AES_TAG_SIZE);
    if (!plaintext) { EVP_CIPHER_CTX_free(ctx); free(ciphertext); return false; }

    EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, AES_IV_SIZE, NULL);
    EVP_DecryptInit_ex(ctx, NULL, NULL, aes_key, iv);
    EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, (int)cipher_len);
    int plain_len = len;

    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, AES_TAG_SIZE, tag) != 1 ||
        EVP_DecryptFinal_ex(ctx, plaintext + plain_len, &len) <= 0) {
        printf("  [DECRYPT] Error: decryption failed (wrong key or tampered data).\n");
        EVP_CIPHER_CTX_free(ctx);
        free(plaintext);
        free(ciphertext);
        return false;
    }
    plain_len += len;
    EVP_CIPHER_CTX_free(ctx);

    size_t orig_name_len = strlen(enc_filename);
    char orig_filename[256];
    if (orig_name_len > 4 && strcmp(enc_filename + orig_name_len - 4, ".enc") == 0) {
        memcpy(orig_filename, enc_filename, orig_name_len - 4);
        orig_filename[orig_name_len - 4] = '\0';
    } else {
        snprintf(orig_filename, sizeof(orig_filename), "%s.dec", enc_filename);
    }

    char out_path[512];
    snprintf(out_path, sizeof(out_path), "%s/%s", vault_dir, orig_filename);
    FILE *fout = fopen(out_path, "wb");
    if (!fout) {
        printf("  [DECRYPT] Error: cannot create output file.\n");
        free(plaintext);
        free(ciphertext);
        return false;
    }
    fwrite(plaintext, 1, (size_t)plain_len, fout);
    fclose(fout);

    free(plaintext);
    free(ciphertext);
    printf("  [DECRYPT] '%s' -> '%s'\n", enc_filename, orig_filename);
    return true;
}
