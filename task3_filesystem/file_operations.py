"""
ST5004CEM - Task 3: Secure File Management System
Stage 1: Basic File Operations (Foundation)

This script implements a FileManager class that provides create, read,
write, and delete operations within a dedicated storage folder ("vault").
No security features yet — that comes in Stage 2.
"""

import os


# --- Why "Secure" File Systems Need More Than Just Operations ---
#
# A real file management system does more than just create/read/write/delete:
#
#   - Authentication: Who is making this request? Without auth, anyone
#     who can run the script can access or modify any file.
#   - Authorization: Is this user ALLOWED to perform this operation?
#     A regular user shouldn't be able to delete another user's files.
#   - Audit Logging: Who did what, and when? Essential for detecting
#     unauthorized access after the fact.
#   - Encryption: Sensitive files should be unreadable without a key,
#     even if someone gains filesystem access.
#
# This stage builds the raw file operations. Stages 2-4 will layer
# authentication, permissions, encryption, and audit logging on top.


class FileManager:
    """
    A simple file manager that operates within a dedicated vault folder.

    All file paths are relative to the vault directory, preventing
    accidental access to files outside it.
    """

    def __init__(self, vault_dir="vault"):
        """
        Initialize the FileManager and create the vault folder if needed.

        Args:
            vault_dir: path to the storage directory (relative to this script).
        """
        self.vault_dir = vault_dir
        # os.makedirs creates the folder (and any parent folders) if needed.
        # exist_ok=True means it won't error if the folder already exists.
        os.makedirs(self.vault_dir, exist_ok=True)
        print(f"[FileManager] Vault directory ready: {self.vault_dir}/\n")

    def _full_path(self, filename):
        """Return the full path to a file inside the vault."""
        # os.path.join safely combines paths with the correct separator
        # (backslash on Windows, forward slash on Linux).
        return os.path.join(self.vault_dir, filename)

    def create_file(self, filename, content):
        """
        Create a new file with the given content.

        Args:
            filename: name of the file to create.
            content: text content to write into the file.

        Returns:
            True on success, False on failure.
        """
        path = self._full_path(filename)

        try:
            # 'x' mode = exclusive creation. It will error if the file
            # already exists, preventing accidental overwrites.
            with open(path, "x") as f:
                f.write(content)
            print(f"  [CREATE] '{filename}' created successfully.")
            return True

        except FileExistsError:
            print(f"  [CREATE] Error: '{filename}' already exists. Use write_file() to modify it.")
            return False

        except Exception as e:
            print(f"  [CREATE] Error: {e}")
            return False

    def read_file(self, filename):
        """
        Read and return the contents of a file.

        Args:
            filename: name of the file to read.

        Returns:
            The file content as a string, or None if the file doesn't exist.
        """
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
        """
        Write content to an existing file (overwrites current content).

        Args:
            filename: name of the file to write to.
            content: new text content to write.

        Returns:
            True on success, False on failure.
        """
        path = self._full_path(filename)

        if not os.path.exists(path):
            print(f"  [WRITE] Error: '{filename}' does not exist. Use create_file() first.")
            return False

        try:
            # 'w' mode = write (overwrites existing content).
            with open(path, "w") as f:
                f.write(content)
            print(f"  [WRITE] '{filename}' updated successfully.")
            return True

        except Exception as e:
            print(f"  [WRITE] Error: {e}")
            return False

    def delete_file(self, filename):
        """
        Delete a file from the vault.

        Args:
            filename: name of the file to delete.

        Returns:
            True on success, False on failure.
        """
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

    def list_files(self):
        """List all files currently in the vault."""
        try:
            files = os.listdir(self.vault_dir)
            if files:
                print(f"  [LIST] Files in vault: {files}")
            else:
                print(f"  [LIST] Vault is empty.")
            return files

        except Exception as e:
            print(f"  [LIST] Error: {e}")
            return []


# ============================================================================
# Demo: Exercise all operations to show they work
# ============================================================================

def main():
    print("=== Stage 1: Basic File Operations ===\n")

    fm = FileManager()

    # --- Create files ---
    print("--- Step 1: Creating files ---")
    fm.create_file("notes.txt", "This is my first file in the vault.")
    fm.create_file("data.csv", "name,age\nAlice,30\nBob,25")
    fm.list_files()

    # --- Read files ---
    print("\n--- Step 2: Reading files ---")
    content1 = fm.read_file("notes.txt")
    print(f"  Content of notes.txt: \"{content1}\"")

    content2 = fm.read_file("data.csv")
    print(f"  Content of data.csv:\n{content2}")

    # Try reading a file that doesn't exist.
    print("\n--- Step 3: Reading a non-existent file ---")
    fm.read_file("missing.txt")

    # --- Write/overwrite an existing file ---
    print("\n--- Step 4: Updating notes.txt ---")
    fm.write_file("notes.txt", "Updated content: this file has been modified.")
    updated = fm.read_file("notes.txt")
    print(f"  New content: \"{updated}\"")

    # --- Try writing to a non-existent file ---
    print("\n--- Step 5: Writing to a non-existent file ---")
    fm.write_file("ghost.txt", "This should fail.")

    # --- Delete a file ---
    print("\n--- Step 6: Deleting data.csv ---")
    fm.delete_file("data.csv")
    fm.list_files()

    # --- Try deleting a file that doesn't exist ---
    print("\n--- Step 7: Deleting a non-existent file ---")
    fm.delete_file("data.csv")

    print("\n--- Final vault state ---")
    fm.list_files()

    print()
    print("Stage 1 complete. No security features yet — anyone can do")
    print("anything. Stage 2 adds user authentication.")


if __name__ == "__main__":
    main()
