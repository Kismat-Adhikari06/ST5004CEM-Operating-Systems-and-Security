"""
ST5004CEM - Task 3: Secure File Management System
Stage 4: File Encryption/Decryption

This script adds encryption capability to the file system using
Fernet symmetric encryption from the cryptography library.

INSTALL REQUIRED LIBRARY:
    pip install cryptography
"""

import os


# --- Symmetric vs Asymmetric Encryption ---
#
# Symmetric encryption (used here):
#   Same key is used to BOTH encrypt and decrypt.
#   Fast and efficient. Good for encrypting large files.
#   Problem: How do you share the key securely? If two people
#   have the same key, either could decrypt the other's files.
#
# Asymmetric encryption (RSA, etc.):
#   Uses a key PAIR: public key (encrypt) + private key (decrypt).
#   Slower, but solves the key-sharing problem — you can share your
#   public key freely, and only you can decrypt with your private key.
#   Often used to encrypt a symmetric key, which then encrypts the data
#   (this hybrid approach is what HTTPS/TLS does).
#
# --- Key Management: The Hardest Part ---
#
# Encryption itself is mathematically strong — modern algorithms like
# AES (which Fernet uses) are practically unbreakable by brute force.
# The weak point is almost always KEY MANAGEMENT:
#   - Where do you store the key?
#   - Who has access to it?
#   - How do you back it up without compromising security?
#   - What happens if the key is lost? (Data is gone forever.)
#
# In this demo, we generate and use the key in the same script.
# In a real system, the key would be stored in a secure key vault
# (e.g., AWS KMS, HashiCorp Vault) separate from the encrypted files.


# Try importing cryptography — give a helpful message if not installed.
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


def generate_key():
    """
    Generate a new Fernet encryption key.

    Returns:
        A URL-safe base64-encoded 32-byte key (as bytes).

    WARNING: In a real system, store this key securely (key vault,
    hardware security module, etc.). Never hardcode it or store it
    alongside the encrypted files.
    """
    return Fernet.generate_key()


def encrypt_file(filename, key):
    """
    Read a file, encrypt its content, and save as filename.enc.

    Args:
        filename: path to the plain-text file.
        key: Fernet encryption key (bytes).

    Returns:
        Path to the encrypted file, or None on failure.
    """
    try:
        # Read original content.
        with open(filename, "r") as f:
            content = f.read()

        # Create a Fernet cipher with the key and encrypt.
        # Fernet uses AES-128-CBC under the hood with HMAC for
        # authentication (tamper detection).
        cipher = Fernet(key)
        encrypted = cipher.encrypt(content.encode("utf-8"))

        # Save encrypted content to a new file.
        enc_filename = filename + ".enc"
        with open(enc_filename, "wb") as f:
            f.write(encrypted)

        print(f"  [ENCRYPT] '{filename}' -> '{enc_filename}'")
        return enc_filename

    except Exception as e:
        print(f"  [ENCRYPT] Error: {e}")
        return None


def decrypt_file(enc_filename, key):
    """
    Read an encrypted file, decrypt it, and save as the original name.

    Args:
        enc_filename: path to the .enc encrypted file.
        key: Fernet encryption key (bytes).

    Returns:
        Path to the decrypted file, or None on failure.
    """
    try:
        # Read encrypted content.
        with open(enc_filename, "rb") as f:
            encrypted = f.read()

        # Decrypt — this will raise an error if the key is wrong
        # or the data has been tampered with.
        cipher = Fernet(key)
        decrypted = cipher.decrypt(encrypted).decode("utf-8")

        # Save decrypted content back to the original filename.
        # Remove the .enc extension to get the original name.
        if enc_filename.endswith(".enc"):
            orig_filename = enc_filename[:-4]
        else:
            orig_filename = enc_filename + ".dec"

        with open(orig_filename, "w") as f:
            f.write(decrypted)

        print(f"  [DECRYPT] '{enc_filename}' -> '{orig_filename}'")
        return orig_filename

    except Exception as e:
        print(f"  [DECRYPT] Error: {e}")
        return None


# ============================================================================
# Demo: Encrypt, show encrypted content, decrypt, wrong-key test
# ============================================================================

def main():
    if not CRYPTO_AVAILABLE:
        print("ERROR: The 'cryptography' library is not installed.")
        print("Install it with: pip install cryptography")
        return

    print("=== Stage 4: File Encryption/Decryption ===\n")

    # Generate an encryption key.
    # In production, this would come from a secure key store.
    print("--- Step 1: Generate encryption key ---")
    key = generate_key()
    print(f"  Generated key: {key.decode()}")

    # Create a test file with sensitive content.
    print("\n--- Step 2: Create a sensitive file ---")
    test_file = "vault/secret_data.txt"
    os.makedirs("vault", exist_ok=True)
    with open(test_file, "w") as f:
        f.write("CONFIDENTIAL: Staff salary data\nAlice: $75,000\nBob: $68,000")

    with open(test_file, "r") as f:
        raw = f.read()
    print(f"  Raw content:\n{raw}")

    # Encrypt the file.
    print("\n--- Step 3: Encrypt the file ---")
    enc_file = encrypt_file(test_file, key)

    # Show that the encrypted file is unreadable.
    if enc_file:
        with open(enc_file, "rb") as f:
            enc_content = f.read()
        print(f"  Encrypted content (unreadable bytes):\n{enc_content}\n")

    # Decrypt the file with the correct key.
    print("\n--- Step 4: Decrypt with correct key ---")
    dec_file = decrypt_file(enc_file, key)

    if dec_file:
        with open(dec_file, "r") as f:
            dec_content = f.read()
        print(f"  Recovered content:\n{dec_content}")
        print(f"  Match: {dec_content == raw}")

    # Try decrypting with the WRONG key.
    print("\n--- Step 5: Decrypt with WRONG key (should fail) ---")
    wrong_key = generate_key()  # A different, random key.
    result = decrypt_file(enc_file, wrong_key)
    if result is None:
        print("  Decryption failed as expected — wrong key cannot decrypt the data.")

    print()
    print("Stage 4 complete. Encryption and decryption working correctly.")
    print("Stage 5 will add audit logging to track all file operations.")


if __name__ == "__main__":
    main()
