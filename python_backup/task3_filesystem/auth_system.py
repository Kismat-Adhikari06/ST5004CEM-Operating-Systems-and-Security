"""
ST5004CEM - Task 3: Secure File Management System
Stage 2: User Authentication System

This script implements a UserAuth class that manages user registration
and login with password hashing. It will gate access to file operations
in later stages.
"""

import hashlib
import os
import secrets


# --- Why Password Hashing Matters ---
#
# NEVER store passwords in plain text. If an attacker gains access to
# the database (or in our case, the user store), they would instantly
# see every user's password. Worse, many people reuse passwords across
# sites, so one breach compromises many accounts.
#
# Hashing is a one-way function: it transforms a password into a fixed-
# length string of characters that CANNOT be reversed to get the original.
#
#   hash("password123") -> "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"
#
# To verify a password, we hash the input and compare it to the stored
# hash. If they match, the password is correct — without ever storing
# or seeing the actual password.
#
# We also use a "salt" (random data mixed into the hash) to prevent
# "rainbow table" attacks, where precomputed hash tables are used to
# crack common passwords.


class UserAuth:
    """
    Manages user registration, login, and session tracking.

    Users are stored in-memory for this demo. In a real system,
    they would be stored in a database.
    """

    def __init__(self):
        self.users = {}          # {username: {"password_hash": ..., "salt": ..., "role": ...}}
        self.current_user = None  # Currently logged-in username (or None).

    def _hash_password(self, password, salt=None):
        """
        Hash a password with a salt using SHA-256.

        Args:
            password: the plain-text password to hash.
            salt: random bytes to mix in. Generated if not provided.

        Returns:
            (hex_digest, salt) tuple.
        """
        if salt is None:
            # os.urandom generates cryptographically strong random bytes.
            salt = os.urandom(16)

        # Combine salt + password, then hash with SHA-256.
        # The salt ensures that even identical passwords produce
        # different hashes, defeating precomputed rainbow tables.
        hash_input = salt + password.encode("utf-8")
        digest = hashlib.sha256(hash_input).hexdigest()

        return digest, salt

    def register_user(self, username, password, role="other"):
        """
        Register a new user with a hashed password.

        Args:
            username: unique username.
            password: plain-text password (will be hashed immediately).
            role: permission level ("owner", "group", or "other").

        Returns:
            True on success, False if username already exists.
        """
        if username in self.users:
            print(f"  [REGISTER] Error: username '{username}' already taken.")
            return False

        # Hash the password right away — plain text never touches storage.
        password_hash, salt = self._hash_password(password)

        self.users[username] = {
            "password_hash": password_hash,
            "salt": salt,
            "role": role,
        }

        print(f"  [REGISTER] User '{username}' registered successfully (role: {role}).")
        return True

    def login(self, username, password):
        """
        Attempt to log in a user.

        IMPORTANT: The error message is always "invalid credentials"
        regardless of whether the username or password was wrong.
        This prevents "username enumeration" — an attacker probing
        which usernames exist by checking for different error messages.

        Args:
            username: the username to authenticate.
            password: the plain-text password to verify.

        Returns:
            True on success, False on failure.
        """
        # Check if the user exists.
        if username not in self.users:
            print(f"  [LOGIN] Invalid credentials.")
            return False

        # Hash the provided password with the stored salt and compare.
        stored = self.users[username]
        input_hash, _ = self._hash_password(password, salt=stored["salt"])

        if input_hash != stored["password_hash"]:
            print(f"  [LOGIN] Invalid credentials.")
            return False

        # Success — set the current session.
        self.current_user = username
        print(f"  [LOGIN] Welcome, {username}! (role: {stored['role']})")
        return True

    def logout(self):
        """Log out the current user."""
        if self.current_user:
            print(f"  [LOGOUT] User '{self.current_user}' logged out.")
            self.current_user = None
        else:
            print(f"  [LOGOUT] No user is currently logged in.")

    def get_current_user(self):
        """Return the currently logged-in username, or None."""
        return self.current_user

    def get_user_role(self, username):
        """Return the role of a user, or None if not found."""
        if username in self.users:
            return self.users[username]["role"]
        return None


# ============================================================================
# Demo: Register users, test login success and failure
# ============================================================================

def main():
    print("=== Stage 2: User Authentication System ===\n")

    auth = UserAuth()

    # --- Register users with different roles ---
    print("--- Step 1: Registering users ---")
    auth.register_user("alice", "securePass123", role="owner")
    auth.register_user("bob", "myPassword456", role="group")
    auth.register_user("charlie", "charliePass789", role="other")

    # Try registering a duplicate username.
    print("\n--- Step 2: Attempting duplicate registration ---")
    auth.register_user("alice", "differentPassword", role="other")

    # --- Successful login ---
    print("\n--- Step 3: Successful login (alice) ---")
    auth.login("alice", "securePass123")
    print(f"  Current user: {auth.get_current_user()}")
    print(f"  Role: {auth.get_user_role('alice')}")

    # --- Logout ---
    print("\n--- Step 4: Logout ---")
    auth.logout()
    print(f"  Current user: {auth.get_current_user()}")

    # --- Failed login: wrong password ---
    print("\n--- Step 5: Failed login — wrong password ---")
    auth.login("bob", "wrongPassword")

    # --- Failed login: nonexistent username ---
    print("\n--- Step 6: Failed login — nonexistent user ---")
    auth.login("nobody", "anyPassword")

    # Note: both failures show "invalid credentials" — same message
    # to prevent username enumeration.

    print()
    print("Stage 2 complete. Authentication is ready.")
    print("Stage 3 will add file permissions using these roles.")


if __name__ == "__main__":
    main()
