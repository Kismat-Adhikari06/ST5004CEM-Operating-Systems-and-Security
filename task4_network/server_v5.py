"""
ST5004CEM - Task 4: Networking
Stage 5: Hardened Multi-Client Server (Final Stage)

This server adds defensive error handling, connection timeouts, and
graceful shutdown — ensuring ONE misbehaving client never crashes
the server or affects other clients.
"""

import socket
import json
import threading
import time


# --- Why Assume Every Client Can Misbehave? ---
#
# In production, the server cannot trust ANY client:
#   - A client might crash mid-message (partial JSON).
#   - A client might go silent and hold a thread forever.
#   - A client might flood the server with garbage data.
#   - A network hiccup might disconnect a client without warning.
#
# If the server doesn't handle ALL of these gracefully, one bad
# client can: crash the server, leak memory (zombie threads),
# or starve other clients of resources. The server must be
# DEFENSIVE: wrap everything in try/except, use timeouts, and
# always clean up resources in finally blocks.

HOST = "127.0.0.1"
PORT = 5000
CLIENT_TIMEOUT = 60  # Seconds of silence before closing a connection.

USERS = {
    "alice": "password123",
    "bob": "bobPass456",
    "charlie": "charlie789",
}


def handle_command(request, is_authenticated):
    """Parse and execute a command. Returns a response dict."""
    try:
        data = json.loads(request)
    except (json.JSONDecodeError, ValueError):
        return {"status": "error", "error": "Invalid JSON format"}

    if not isinstance(data, dict) or "command" not in data:
        return {"status": "error", "error": "Missing 'command' field"}

    command = data["command"]

    if command == "LOGIN":
        if "username" not in data or "password" not in data:
            return {"status": "error", "error": "LOGIN requires 'username' and 'password' fields"}
        username = data["username"]
        password = data["password"]
        if username in USERS and USERS[username] == password:
            return {"status": "ok", "result": "Login successful", "authenticated": True, "username": username}
        else:
            return {"status": "error", "error": "Invalid credentials"}

    if not is_authenticated:
        return {"status": "error", "error": "Not authenticated. Please LOGIN first."}

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
    """
    Handle one client in its own thread.

    ALL exceptions are caught so that a misbehaving client never
    crashes the server or affects other threads.
    """
    print(f"[Server] Client {client_id} ({client_address}) connected.")

    is_authenticated = False
    username = None

    try:
        # Set a timeout on the socket — if the client goes silent
        # for CLIENT_TIMEOUT seconds, recv() raises socket.timeout
        # and we close the connection instead of hanging forever.
        client_socket.settimeout(CLIENT_TIMEOUT)

        while True:
            try:
                raw_data = client_socket.recv(4096)
            except socket.timeout:
                print(f"[Server] Client {client_id} timed out ({CLIENT_TIMEOUT}s of silence). Closing.")
                break

            if not raw_data:
                break  # Client disconnected cleanly.

            # Decode and validate the data.
            try:
                request = raw_data.decode("utf-8")
            except UnicodeDecodeError:
                # Client sent garbage bytes that aren't valid UTF-8.
                error_response = json.dumps({"status": "error", "error": "Invalid encoding"})
                client_socket.sendall(error_response.encode("utf-8"))
                print(f"[Server] Client {client_id} sent invalid bytes. Sent error response.")
                continue

            print(f"[Server] Client {client_id} ({username or 'unknown'}) sent: {request}")

            response = handle_command(request, is_authenticated)

            if response.get("authenticated"):
                is_authenticated = True
                username = response.get("username", "unknown")

            response_json = json.dumps(response)
            client_socket.sendall(response_json.encode("utf-8"))
            print(f"[Server] Sent to client {client_id}: {response_json}")

    except ConnectionResetError:
        print(f"[Server] Client {client_id} connection reset by peer.")
    except ConnectionAbortedError:
        print(f"[Server] Client {client_id} connection aborted.")
    except BrokenPipeError:
        print(f"[Server] Client {client_id} pipe broken (client gone).")
    except OSError as e:
        print(f"[Server] Client {client_id} OS error: {e}")
    except Exception as e:
        # Catch-all for any unexpected error — log it and move on.
        # This is the key defensive pattern: no single client can crash
        # the server because ALL exceptions are contained within the thread.
        print(f"[Server] Client {client_id} unexpected error: {type(e).__name__}: {e}")
    finally:
        try:
            client_socket.close()
        except Exception:
            pass  # Socket might already be closed — ignore.
        print(f"[Server] Client {client_id} ({username or 'unknown'}) connection closed.\n")


def main():
    print("=== Stage 5: Hardened Multi-Client Server (Final) ===\n")
    print(f"Registered users: {list(USERS.keys())}")
    print(f"Client timeout: {CLIENT_TIMEOUT}s\n")

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
        print("\n[Server] Ctrl+C received. Shutting down gracefully...")
    except Exception as e:
        print(f"\n[Server] Fatal error: {e}")
    finally:
        server_socket.close()
        print("[Server] Server socket closed. Goodbye.")


if __name__ == "__main__":
    main()
