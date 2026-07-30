"""
ST5004CEM - Task 4: Networking
Stage 4: Multi-Client Server with Authentication

This server requires clients to authenticate (LOGIN) before they
can use any commands. Each connection tracks its own auth state.
"""

import socket
import json
import hashlib
import threading


# --- Why Authentication Per-Connection? ---
#
# Each TCP connection is independent — the server doesn't automatically
# know who is on the other end just because they connected. Anyone who
# can reach the port could send commands. Authentication forces each
# client to PROVE their identity before the server will do anything.
#
# In a real networked service (web app, API, database), anyone on the
# internet can reach the port. Without auth, an attacker could:
#   - Read other users' data.
#   - Modify or delete files.
#   - Execute privileged operations.
#
# Each connection must authenticate independently because:
#   - Different users may connect at different times.
#   - One user's credentials don't apply to another's connection.
#   - If one client disconnects, other authenticated clients still work.

HOST = "127.0.0.1"
PORT = 5000

# Hardcoded users for this demo.
# In Task 3, we used password hashing — here we keep it simple since
# the focus is the network auth flow, not the hashing itself.
USERS = {
    "alice": "password123",
    "bob": "bobPass456",
    "charlie": "charlie789",
}


def hash_password(password):
    """Simple SHA-256 hash for password comparison."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def handle_command(request, is_authenticated):
    """
    Parse and execute a command if the client is authenticated.

    LOGIN commands are always allowed (you need to login before anything).
    All other commands require authentication.
    """
    try:
        data = json.loads(request)
    except json.JSONDecodeError:
        return {"status": "error", "error": "Invalid JSON format"}

    if "command" not in data:
        return {"status": "error", "error": "Missing 'command' field"}

    command = data["command"]

    # --- LOGIN command (always allowed, even before auth) ---
    if command == "LOGIN":
        if "username" not in data or "password" not in data:
            return {"status": "error", "error": "LOGIN requires 'username' and 'password' fields"}

        username = data["username"]
        password = data["password"]

        # Check credentials against our user database.
        if username in USERS and USERS[username] == password:
            return {"status": "ok", "result": "Login successful", "authenticated": True, "username": username}
        else:
            return {"status": "error", "error": "Invalid credentials"}

    # --- All other commands require authentication ---
    if not is_authenticated:
        return {"status": "error", "error": "Not authenticated. Please LOGIN first."}

    # Validate "data" field for non-login commands.
    if "data" not in data:
        return {"status": "error", "error": "Missing 'data' field"}

    payload = data["data"]
    if not isinstance(payload, str):
        return {"status": "error", "error": "'data' field must be a string"}

    if command == "ECHO":
        return {"status": "ok", "result": payload}
    elif command == "UPPERCASE":
        return {"status": "ok", "result": payload.upper()}
    elif command == "REVERSE":
        return {"status": "ok", "result": payload[::-1]}
    else:
        return {"status": "error", "error": f"Unknown command: '{command}'"}


def handle_client(client_socket, client_address, client_id):
    """Handle one client in its own thread with per-connection auth state."""
    print(f"[Server] Client {client_id} ({client_address}) connected.")

    is_authenticated = False
    username = None

    try:
        while True:
            raw_data = client_socket.recv(4096)
            if not raw_data:
                break

            request = raw_data.decode("utf-8")
            print(f"[Server] Client {client_id} ({username or 'unknown'}) sent: {request}")

            response = handle_command(request, is_authenticated)

            # If LOGIN just succeeded, update this connection's auth state.
            if response.get("authenticated"):
                is_authenticated = True
                username = response.get("username", "unknown")

            response_json = json.dumps(response)
            client_socket.sendall(response_json.encode("utf-8"))
            print(f"[Server] Sent to client {client_id}: {response_json}")

    except ConnectionResetError:
        print(f"[Server] Client {client_id} disconnected abruptly.")
    except Exception as e:
        print(f"[Server] Error with client {client_id}: {e}")
    finally:
        client_socket.close()
        print(f"[Server] Client {client_id} ({username or 'unknown'}) connection closed.\n")


def main():
    print("=== Stage 4: Multi-Client Server with Authentication ===\n")
    print(f"Registered users: {list(USERS.keys())}\n")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}...")
    print("Waiting for clients to connect...\n")

    thread_counter = 0
    counter_lock = threading.Lock()

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            with counter_lock:
                thread_counter += 1
                client_id = thread_counter

            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address, client_id),
                daemon=True,
            )
            thread.start()

    except KeyboardInterrupt:
        print("\n[Server] Shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
