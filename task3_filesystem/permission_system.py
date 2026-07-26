"""
ST5004CEM - Task 3: Secure File Management System
Stage 3: Unix-style File Permission System

This script adds owner/group/others × read/write/execute permissions
to file operations, integrated with the authentication system from Stage 2.
"""

import hashlib
import os


# --- Owner/Group/Others Permission Model ---
#
# Unix file systems use a simple but powerful permission model:
#   - Owner:  the user who owns the file. Usually full access.
#   - Group:  a set of users who share access (e.g., a project team).
#   - Others: everyone else on the system.
#
# Each of these three categories can have three permissions:
#   - Read (r):    view the file's contents.
#   - Write (w):   modify or delete the file.
#   - Execute (x): run the file as a program/script.
#
# This is typically shown as a string like "rwxr-x---":
#   Owner:  rwx (full access)
#   Group:  r-x (read and execute, no write)
#   Others: --- (no access at all)
#
# --- Principle of Least Privilege ---
#
# Give each user the MINIMUM access they need to do their job.
# If someone only needs to read a file, don't give them write access.
# If a file is sensitive, don't give others any access at all.
#
# This limits damage from mistakes ("oops, I deleted the wrong file")
# and from compromised accounts ("the attacker can only read, not write").
# Always start with zero permissions and add only what's needed.


# ============================================================================
# Password Hashing (from Stage 2, kept self-contained)
# ============================================================================

class UserAuth:
    """Simple user authentication with password hashing."""

    def __init__(self):
        self.users = {}
        self.current_user = None

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = os.urandom(16)
        digest = hashlib.sha256(salt + password.encode("utf-8")).hexdigest()
        return digest, salt

    def register_user(self, username, password, role="other"):
        if username in self.users:
            print(f"  [REGISTER] Error: username '{username}' already taken.")
            return False
        password_hash, salt = self._hash_password(password)
        self.users[username] = {"password_hash": password_hash, "salt": salt, "role": role}
        print(f"  [REGISTER] User '{username}' registered (role: {role}).")
        return True

    def login(self, username, password):
        if username not in self.users:
            print(f"  [LOGIN] Invalid credentials.")
            return False
        stored = self.users[username]
        input_hash, _ = self._hash_password(password, salt=stored["salt"])
        if input_hash != stored["password_hash"]:
            print(f"  [LOGIN] Invalid credentials.")
            return False
        self.current_user = username
        print(f"  [LOGIN] Welcome, {username}! (role: {stored['role']})")
        return True

    def logout(self):
        if self.current_user:
            print(f"  [LOGOUT] User '{self.current_user}' logged out.")
            self.current_user = None

    def get_current_user(self):
        return self.current_user

    def get_user_role(self, username):
        return self.users.get(username, {}).get("role")


# ============================================================================
# Permission System
# ============================================================================

class PermissionSystem:
    """
    Manages Unix-style rwx permissions for files in the vault.

    Each file gets a permission record:
        {
            "owner": "alice",
            "permissions": "rw-r-----"
                            ^^^ ^^^ ---
                            ||| |||  others: no access
                            ||| group: read only
                            owner: read + write
        }

    Permission string layout: rwxrwxrwx (9 characters)
        Chars 0-2: owner  (r=read, w=write, x=execute, -=none)
        Chars 3-5: group
        Chars 6-8: others
    """

    def __init__(self):
        self.file_permissions = {}  # {filename: {"owner": ..., "permissions": ...}}

    def set_permissions(self, filename, owner, permissions):
        """
        Set the permissions for a file.

        Args:
            filename: name of the file.
            owner: username of the file's owner.
            permissions: 9-char string like "rw-r-----".
        """
        self.file_permissions[filename] = {
            "owner": owner,
            "permissions": permissions,
        }

    def get_permissions(self, filename):
        """Return the permission record for a file, or None."""
        return self.file_permissions.get(filename)

    def check_permission(self, filename, username, user_role, action):
        """
        Check if a user is allowed to perform an action on a file.

        The check works by determining which category the user falls
        into (owner, group, or others), then checking if that category
        has the requested permission.

        Args:
            filename: name of the file.
            username: name of the user requesting access.
            user_role: the user's role from auth ("owner", "group", "other").
            action: "read", "write", or "execute".

        Returns:
            True if allowed, False if denied.
        """
        record = self.file_permissions.get(filename)
        if not record:
            return False

        perms = record["permissions"]

        # Determine which 3-char segment of the permission string to check.
        # Owner (chars 0-2) has priority if the user IS the file owner,
        # regardless of their system role.
        if username == record["owner"]:
            segment = perms[0:3]  # owner permissions
        elif user_role == "group":
            segment = perms[3:6]  # group permissions
        else:
            segment = perms[6:9]  # others permissions

        # Map action names to permission characters.
        action_map = {"read": "r", "write": "w", "execute": "x"}
        required = action_map.get(action)

        if required is None:
            return False

        return required in segment


# ============================================================================
# Secure FileManager (combines file ops + auth + permissions)
# ============================================================================

class SecureFileManager:
    """
    File manager that requires authentication and checks permissions
    before performing any file operation.
    """

    def __init__(self, vault_dir="vault"):
        self.vault_dir = vault_dir
        os.makedirs(self.vault_dir, exist_ok=True)
        self.auth = UserAuth()
        self.permissions = PermissionSystem()

    def _full_path(self, filename):
        return os.path.join(self.vault_dir, filename)

    def _require_login(self):
        """Check that a user is logged in. Returns username or None."""
        user = self.auth.get_current_user()
        if user is None:
            print("  [ERROR] No user logged in. Please log in first.")
            return None
        return user

    def create_file(self, filename, content):
        """Create a file owned by the currently logged-in user."""
        user = self._require_login()
        if user is None:
            return False

        path = self._full_path(filename)
        try:
            with open(path, "x") as f:
                f.write(content)

            # Default permissions: owner can read/write, nobody else can do anything.
            self.permissions.set_permissions(filename, owner=user, permissions="rw-------")
            print(f"  [CREATE] '{filename}' created (owner: {user}, permissions: rw-------).")
            return True

        except FileExistsError:
            print(f"  [CREATE] Error: '{filename}' already exists.")
            return False
        except Exception as e:
            print(f"  [CREATE] Error: {e}")
            return False

    def read_file(self, filename):
        """Read a file, checking read permission first."""
        user = self._require_login()
        if user is None:
            return None

        role = self.auth.get_user_role(user)
        if not self.permissions.check_permission(filename, user, role, "read"):
            print(f"  [READ] Denied: '{user}' does not have read permission on '{filename}'.")
            return None

        path = self._full_path(filename)
        try:
            with open(path, "r") as f:
                content = f.read()
            print(f"  [READ] '{filename}' read successfully.")
            return content
        except FileNotFoundError:
            print(f"  [READ] Error: '{filename}' not found.")
            return None
        except Exception as e:
            print(f"  [READ] Error: {e}")
            return None

    def write_file(self, filename, content):
        """Write to a file, checking write permission first."""
        user = self._require_login()
        if user is None:
            return False

        role = self.auth.get_user_role(user)
        if not self.permissions.check_permission(filename, user, role, "write"):
            print(f"  [WRITE] Denied: '{user}' does not have write permission on '{filename}'.")
            return False

        path = self._full_path(filename)
        try:
            with open(path, "w") as f:
                f.write(content)
            print(f"  [WRITE] '{filename}' updated successfully.")
            return True
        except FileNotFoundError:
            print(f"  [WRITE] Error: '{filename}' does not exist.")
            return False
        except Exception as e:
            print(f"  [WRITE] Error: {e}")
            return False

    def delete_file(self, filename):
        """Delete a file, checking write permission first."""
        user = self._require_login()
        if user is None:
            return False

        role = self.auth.get_user_role(user)
        if not self.permissions.check_permission(filename, user, role, "write"):
            print(f"  [DELETE] Denied: '{user}' does not have write permission on '{filename}'.")
            return False

        path = self._full_path(filename)
        try:
            os.remove(path)
            print(f"  [DELETE] '{filename}' deleted successfully.")
            return True
        except FileNotFoundError:
            print(f"  [DELETE] Error: '{filename}' not found.")
            return False
        except Exception as e:
            print(f"  [DELETE] Error: {e}")
            return False


# ============================================================================
# Demo: Full permission workflow
# ============================================================================

def main():
    print("=== Stage 3: File Permission System ===\n")

    fm = SecureFileManager()

    # --- Register users ---
    print("--- Setting up users ---")
    fm.auth.register_user("alice", "alicePass", role="owner")
    fm.auth.register_user("bob", "bobPass", role="group")
    fm.auth.register_user("charlie", "charliePass", role="other")

    # --- Alice creates a file ---
    print("\n--- Step 1: Alice logs in and creates a file ---")
    fm.auth.login("alice", "alicePass")
    fm.create_file("secret.txt", "This is Alice's private file.")

    # --- Alice can read and write her own file ---
    print("\n--- Step 2: Alice reads and writes her own file ---")
    fm.read_file("secret.txt")
    fm.write_file("secret.txt", "Alice updated her file.")

    # --- Bob tries to access the file (group role) ---
    print("\n--- Step 3: Alice logs out, Bob logs in ---")
    fm.auth.logout()

    fm.auth.login("bob", "bobPass")

    print("\n--- Step 4: Bob tries to read Alice's file (group=r, should succeed) ---")
    fm.read_file("secret.txt")

    print("\n--- Step 5: Bob tries to write to Alice's file (group has no write, should deny) ---")
    fm.write_file("secret.txt", "Bob tried to overwrite this.")

    # --- Charlie tries to access the file (other role) ---
    print("\n--- Step 6: Bob logs out, Charlie logs in ---")
    fm.auth.logout()

    fm.auth.login("charlie", "charliePass")

    print("\n--- Step 7: Charlie tries to read (others=no access, should deny) ---")
    fm.read_file("secret.txt")

    # --- Alice changes permissions to allow others to read ---
    print("\n--- Step 8: Charlie logs out, Alice logs in to change permissions ---")
    fm.auth.logout()

    fm.auth.login("alice", "alicePass")

    print("\n--- Step 9: Alice changes permissions to rw-r--r-- (others can now read) ---")
    fm.permissions.set_permissions("secret.txt", owner="alice", permissions="rw-r--r--")
    print(f"  New permissions: {fm.permissions.get_permissions('secret.txt')['permissions']}")

    # --- Charlie tries again with new permissions ---
    print("\n--- Step 10: Alice logs out, Charlie logs in again ---")
    fm.auth.logout()

    fm.auth.login("charlie", "charliePass")

    print("\n--- Step 11: Charlie tries to read (others=r, should now succeed) ---")
    fm.read_file("secret.txt")

    print("\n--- Step 12: Charlie tries to write (others still no write, denied) ---")
    fm.write_file("secret.txt", "Charlie tried to overwrite this.")

    print()
    print("Stage 3 complete. Permission system working.")
    print("Stage 4 will add encryption and audit logging.")


if __name__ == "__main__":
    main()
