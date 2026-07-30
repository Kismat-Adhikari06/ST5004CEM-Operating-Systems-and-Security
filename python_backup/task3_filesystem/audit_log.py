"""
ST5004CEM - Task 3: Secure File Management System
Stage 5: Audit Logging (Final Stage)

This script adds comprehensive audit logging that records every
significant action across authentication, file operations, encryption,
and permission changes.
"""

import hashlib
import os
from datetime import datetime


# --- Why Audit Logging Matters for Security ---
#
# Audit logs answer three critical questions after a security incident:
#
#   1. WHO did it?    -> The username field identifies the actor.
#   2. WHAT did they do? -> The action and target file describe the event.
#   3. WHEN did it happen? -> The timestamp reconstructs the timeline.
#
# Without logs, you have no way to know:
#   - If an attacker accessed sensitive data.
#   - Which accounts were compromised.
#   - How the attacker moved through the system (lateral movement).
#
# Audit logs also DETECT threats in real time:
#   - Repeated permission_denied events = someone probing for access.
#   - Login failures followed by a success = possible brute force.
#   - Encryption of unusual files = potential data exfiltration prep.
#
# Logs must be APPEND-ONLY (write but never modify/delete) so attackers
# can't cover their tracks. In production, logs go to a separate
# secure server (SIEM) that the attacker can't access.


# ============================================================================
# Audit Logger
# ============================================================================

class AuditLogger:
    """
    Records every significant action to an append-only log file.

    Each log entry includes: timestamp, username, action, target, result.
    """

    def __init__(self, log_file="audit_log.txt"):
        self.log_file = log_file
        # Create the log file if it doesn't exist.
        if not os.path.exists(log_file):
            with open(log_file, "w") as f:
                f.write("=== AUDIT LOG ===\n\n")

    def log(self, username, action, target="-", result="success"):
        """
        Append a log entry to the audit log.

        Args:
            username: who performed the action (or "unknown").
            action: what was done (login, read, write, etc.).
            target: file or resource affected (or "-" if none).
            result: "success" or "failure".
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] User: {username:<10} | Action: {action:<20} | Target: {target:<20} | Result: {result}"

        with open(self.log_file, "a") as f:
            f.write(entry + "\n")

    def get_all_logs(self):
        """Return all log entries as a list of strings."""
        with open(self.log_file, "r") as f:
            return f.readlines()

    def get_logs_for_user(self, username):
        """Return only log entries matching a specific username."""
        all_logs = self.get_all_logs()
        return [line for line in all_logs if f"User: {username}" in line]

    def get_failed_attempts(self):
        """Return only log entries where the result was 'failure'."""
        all_logs = self.get_all_logs()
        return [line for line in all_logs if "Result: failure" in line]

    def get_logs_by_action(self, action):
        """Return only log entries matching a specific action type."""
        all_logs = self.get_all_logs()
        return [line for line in all_logs if f"Action: {action}" in line]

    def print_log(self, entries=None):
        """Pretty-print log entries."""
        if entries is None:
            entries = self.get_all_logs()
        print("".join(entries))


# ============================================================================
# Password Hashing (from Stage 2)
# ============================================================================

class UserAuth:
    """Simple user authentication with password hashing."""

    def __init__(self, logger):
        self.users = {}
        self.current_user = None
        self.logger = logger

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = os.urandom(16)
        digest = hashlib.sha256(salt + password.encode("utf-8")).hexdigest()
        return digest, salt

    def register_user(self, username, password, role="other"):
        if username in self.users:
            self.logger.log(username, "register", result="failure")
            print(f"  [REGISTER] Error: username '{username}' already taken.")
            return False
        password_hash, salt = self._hash_password(password)
        self.users[username] = {"password_hash": password_hash, "salt": salt, "role": role}
        self.logger.log(username, "register", result="success")
        print(f"  [REGISTER] User '{username}' registered (role: {role}).")
        return True

    def login(self, username, password):
        if username not in self.users:
            self.logger.log(username or "unknown", "login", result="failure")
            print(f"  [LOGIN] Invalid credentials.")
            return False
        stored = self.users[username]
        input_hash, _ = self._hash_password(password, salt=stored["salt"])
        if input_hash != stored["password_hash"]:
            self.logger.log(username, "login", result="failure")
            print(f"  [LOGIN] Invalid credentials.")
            return False
        self.current_user = username
        self.logger.log(username, "login", result="success")
        print(f"  [LOGIN] Welcome, {username}! (role: {stored['role']})")
        return True

    def logout(self):
        if self.current_user:
            self.logger.log(self.current_user, "logout", result="success")
            print(f"  [LOGOUT] User '{self.current_user}' logged out.")
            self.current_user = None

    def get_current_user(self):
        return self.current_user

    def get_user_role(self, username):
        return self.users.get(username, {}).get("role")


# ============================================================================
# Permission System (from Stage 3)
# ============================================================================

class PermissionSystem:
    """Unix-style permission checking."""

    def __init__(self, logger):
        self.file_permissions = {}
        self.logger = logger

    def set_permissions(self, filename, owner, permissions, changed_by=None):
        self.file_permissions[filename] = {"owner": owner, "permissions": permissions}
        user = changed_by or owner
        self.logger.log(user, "permission_changed", filename, "success")
        print(f"  [PERMS] '{filename}' permissions set to {permissions}")

    def get_permissions(self, filename):
        return self.file_permissions.get(filename)

    def check_permission(self, filename, username, user_role, action):
        record = self.file_permissions.get(filename)
        if not record:
            return False
        perms = record["permissions"]
        if username == record["owner"]:
            segment = perms[0:3]
        elif user_role == "group":
            segment = perms[3:6]
        else:
            segment = perms[6:9]
        action_map = {"read": "r", "write": "w", "execute": "x"}
        required = action_map.get(action)
        if required is None:
            return False
        return required in segment


# ============================================================================
# Encryption System (from Stage 4)
# ============================================================================

class EncryptionSystem:
    """File encryption using Fernet symmetric encryption."""

    def __init__(self, logger):
        self.logger = logger
        try:
            from cryptography.fernet import Fernet
            self.Fernet = Fernet
            self.available = True
        except ImportError:
            self.available = False
            print("  [WARNING] cryptography library not installed. Run: pip install cryptography")

    def generate_key(self):
        return self.Fernet.generate_key()

    def encrypt_file(self, filename, key, username="unknown"):
        if not self.available:
            self.logger.log(username, "encrypt", filename, "failure")
            return None
        try:
            with open(filename, "r") as f:
                content = f.read()
            cipher = self.Fernet(key)
            encrypted = cipher.encrypt(content.encode("utf-8"))
            enc_filename = filename + ".enc"
            with open(enc_filename, "wb") as f:
                f.write(encrypted)
            self.logger.log(username, "encrypt", filename, "success")
            print(f"  [ENCRYPT] '{filename}' -> '{enc_filename}'")
            return enc_filename
        except Exception as e:
            self.logger.log(username, "encrypt", filename, "failure")
            print(f"  [ENCRYPT] Error: {e}")
            return None

    def decrypt_file(self, enc_filename, key, username="unknown"):
        if not self.available:
            self.logger.log(username, "decrypt", enc_filename, "failure")
            return None
        try:
            with open(enc_filename, "rb") as f:
                encrypted = f.read()
            cipher = self.Fernet(key)
            decrypted = cipher.decrypt(encrypted).decode("utf-8")
            orig_filename = enc_filename[:-4] if enc_filename.endswith(".enc") else enc_filename + ".dec"
            with open(orig_filename, "w") as f:
                f.write(decrypted)
            self.logger.log(username, "decrypt", enc_filename, "success")
            print(f"  [DECRYPT] '{enc_filename}' -> '{orig_filename}'")
            return orig_filename
        except Exception as e:
            self.logger.log(username, "decrypt", enc_filename, "failure")
            print(f"  [DECRYPT] Error: {e}")
            return None


# ============================================================================
# Secure FileManager (ties everything together with logging)
# ============================================================================

class SecureFileManager:
    """File manager with auth, permissions, encryption, and audit logging."""

    def __init__(self, vault_dir="vault"):
        self.vault_dir = vault_dir
        os.makedirs(self.vault_dir, exist_ok=True)

        self.logger = AuditLogger()
        self.auth = UserAuth(self.logger)
        self.permissions = PermissionSystem(self.logger)
        self.encryption = EncryptionSystem(self.logger)

    def _full_path(self, filename):
        return os.path.join(self.vault_dir, filename)

    def _require_login(self):
        user = self.auth.get_current_user()
        if user is None:
            print("  [ERROR] No user logged in.")
            return None
        return user

    def create_file(self, filename, content):
        user = self._require_login()
        if user is None:
            return False
        path = self._full_path(filename)
        try:
            with open(path, "x") as f:
                f.write(content)
            self.permissions.set_permissions(filename, owner=user, permissions="rw-------", changed_by=user)
            self.logger.log(user, "create", filename, "success")
            print(f"  [CREATE] '{filename}' created (owner: {user}).")
            return True
        except FileExistsError:
            self.logger.log(user, "create", filename, "failure")
            print(f"  [CREATE] Error: '{filename}' already exists.")
            return False
        except Exception as e:
            self.logger.log(user, "create", filename, "failure")
            print(f"  [CREATE] Error: {e}")
            return False

    def read_file(self, filename):
        user = self._require_login()
        if user is None:
            return None
        role = self.auth.get_user_role(user)
        if not self.permissions.check_permission(filename, user, role, "read"):
            self.logger.log(user, "read", filename, "failure")
            print(f"  [READ] Denied: '{user}' does not have read permission on '{filename}'.")
            return None
        path = self._full_path(filename)
        try:
            with open(path, "r") as f:
                content = f.read()
            self.logger.log(user, "read", filename, "success")
            print(f"  [READ] '{filename}' read successfully.")
            return content
        except FileNotFoundError:
            self.logger.log(user, "read", filename, "failure")
            print(f"  [READ] Error: '{filename}' not found.")
            return None

    def write_file(self, filename, content):
        user = self._require_login()
        if user is None:
            return False
        role = self.auth.get_user_role(user)
        if not self.permissions.check_permission(filename, user, role, "write"):
            self.logger.log(user, "write", filename, "failure")
            print(f"  [WRITE] Denied: '{user}' does not have write permission on '{filename}'.")
            return False
        path = self._full_path(filename)
        try:
            with open(path, "w") as f:
                f.write(content)
            self.logger.log(user, "write", filename, "success")
            print(f"  [WRITE] '{filename}' updated successfully.")
            return True
        except FileNotFoundError:
            self.logger.log(user, "write", filename, "failure")
            print(f"  [WRITE] Error: '{filename}' does not exist.")
            return False

    def delete_file(self, filename):
        user = self._require_login()
        if user is None:
            return False
        role = self.auth.get_user_role(user)
        if not self.permissions.check_permission(filename, user, role, "write"):
            self.logger.log(user, "delete", filename, "failure")
            print(f"  [DELETE] Denied: '{user}' does not have write permission on '{filename}'.")
            return False
        path = self._full_path(filename)
        try:
            os.remove(path)
            self.logger.log(user, "delete", filename, "success")
            print(f"  [DELETE] '{filename}' deleted successfully.")
            return True
        except FileNotFoundError:
            self.logger.log(user, "delete", filename, "failure")
            print(f"  [DELETE] Error: '{filename}' not found.")
            return False

    def encrypt_file(self, filename, key):
        user = self._require_login()
        if user is None:
            return None
        path = self._full_path(filename)
        return self.encryption.encrypt_file(path, key, username=user)

    def decrypt_file(self, enc_filename, key):
        user = self._require_login()
        if user is None:
            return None
        path = self._full_path(enc_filename)
        return self.encryption.decrypt_file(path, key, username=user)


# ============================================================================
# Demo: Realistic scenario with full audit trail
# ============================================================================

def main():
    print("=== Stage 5: Audit Logging (Final) ===\n")

    fm = SecureFileManager()

    # Clear any previous log for a fresh demo.
    with open("audit_log.txt", "w") as f:
        f.write("=== AUDIT LOG ===\n\n")

    # Register users.
    print("--- Setting up users ---")
    fm.auth.register_user("alice", "alicePass", role="owner")
    fm.auth.register_user("bob", "bobPass", role="group")

    # --- Alice logs in, creates and encrypts a file ---
    print("\n--- Step 1: Alice logs in and creates a file ---")
    fm.auth.login("alice", "alicePass")
    fm.create_file("financials.txt", "Revenue: $1.2M\nCosts: $800K")

    print("\n--- Step 2: Alice encrypts the file ---")
    enc_key = fm.encryption.generate_key()
    fm.encrypt_file("financials.txt", enc_key)

    # --- Bob tries to access (should be denied) ---
    print("\n--- Step 3: Alice logs out, Bob logs in ---")
    fm.auth.logout()

    fm.auth.login("bob", "bobPass")

    print("\n--- Step 4: Bob tries to read (denied - no permission) ---")
    fm.read_file("financials.txt")

    # --- Alice grants Bob read access ---
    print("\n--- Step 5: Bob logs out, Alice logs in to grant access ---")
    fm.auth.logout()

    fm.auth.login("alice", "alicePass")
    fm.permissions.set_permissions("financials.txt", owner="alice", permissions="rw-r-----", changed_by="alice")

    # --- Bob reads successfully ---
    print("\n--- Step 6: Bob logs in again and reads successfully ---")
    fm.auth.logout()

    fm.auth.login("bob", "bobPass")
    fm.read_file("financials.txt")

    # --- Print the full audit log ---
    print("\n" + "=" * 80)
    print(" FULL AUDIT LOG")
    print("=" * 80)
    fm.logger.print_log()

    # --- Query: failed attempts ---
    print("\n" + "=" * 80)
    print(" FAILED ATTEMPTS ONLY")
    print("=" * 80)
    failed = fm.logger.get_failed_attempts()
    if failed:
        print("".join(failed))
    else:
        print("  (none)")

    # --- Query: alice's activity ---
    print("\n" + "=" * 80)
    print(" ALICE'S ACTIVITY ONLY")
    print("=" * 80)
    alice_logs = fm.logger.get_logs_for_user("alice")
    print("".join(alice_logs))

    print()
    print("Stage 5 complete. Task 3 is fully built across 5 stages:")
    print("  Stage 1: Basic file operations")
    print("  Stage 2: User authentication with password hashing")
    print("  Stage 3: Unix-style permission system (rwx)")
    print("  Stage 4: File encryption/decryption (Fernet)")
    print("  Stage 5: Comprehensive audit logging")


if __name__ == "__main__":
    main()
