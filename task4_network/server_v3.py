"""
ST5004CEM - Task 4: Networking
Stage 3: Multi-Client Server Using Threading

This server handles multiple clients concurrently by spawning a new
thread for each connection. Ties back to Task 1 threading concepts.
"""

import socket
import json
import threading


# --- Why Single-Threaded Servers Fail with Multiple Clients ---
#
# A single-threaded server handles one client at a time:
#   1. Client A connects.
#   2. Server processes Client A's request (maybe slow — large file, etc.)
#   3. Client B connects but must WAIT until Client A is fully done.
#   4. Client C connects — same problem, stuck behind A and B.
#
# This is called "blocking" — one slow or hung client blocks everyone.
# In a real web server, this would mean your website goes down for
# all users because one user has a bad connection.
#
# --- How Threading Fixes This ---
#
# With threading, the server's main loop only handles NEW connections.
# Each client gets its own thread that runs independently:
#   1. Client A connects -> thread_A created to handle it.
#   2. Client B connects -> thread_B created (runs in parallel with A).
#   3. Client C connects -> thread_C created (runs in parallel with A and B).
#
# Each thread blocks only on ITS OWN client's recv(), not others.
# This is exactly what we demonstrated in Task 1 Stage 1 — multiple
# threads running concurrently, each doing its own work independently.

HOST = "127.0.0.1"
PORT = 5000

# Track active threads for cleanup.
active_threads = []
thread_counter = 0
counter_lock = threading.Lock()


def handle_command(request):
    """Parse JSON request and execute the command. Returns a response dict."""
    try:
        data = json.loads(request)
    except json.JSONDecodeError:
        return {"status": "error", "error": "Invalid JSON format"}

    if "command" not in data:
        return {"status": "error", "error": "Missing 'command' field"}
    if "data" not in data:
        return {"status": "error", "error": "Missing 'data' field"}

    command = data["command"]
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
    Handle all communication with one client in its own thread.

    This function runs independently for each connected client.
    Multiple instances run concurrently — each one blocks only on
    its own client's recv(), not others.
    """
    print(f"[Server] Client {client_id} ({client_address}) connected.")

    try:
        while True:
            raw_data = client_socket.recv(4096)
            if not raw_data:
                break  # Client disconnected cleanly.

            request = raw_data.decode("utf-8")
            print(f"[Server] Client {client_id} sent: {request}")

            response = handle_command(request)
            response_json = json.dumps(response)
            client_socket.sendall(response_json.encode("utf-8"))
            print(f"[Server] Sent to client {client_id}: {response_json}")

    except ConnectionResetError:
        print(f"[Server] Client {client_id} disconnected abruptly.")
    except Exception as e:
        print(f"[Server] Error with client {client_id}: {e}")
    finally:
        client_socket.close()
        print(f"[Server] Client {client_id} connection closed.\n")


def main():
    global thread_counter

    print("=== Stage 3: Multi-Client TCP Server (Threaded) ===\n")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # Backlog of 5 — can queue multiple connections.
    print(f"Server listening on {HOST}:{PORT}...")
    print("Waiting for clients to connect...\n")

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            # Assign a unique ID to each client.
            with counter_lock:
                thread_counter += 1
                client_id = thread_counter

            # Spawn a new thread for this client.
            # This is the same threading.Thread() pattern from Task 1,
            # but here each thread handles an independent client.
            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address, client_id),
                daemon=True,  # Thread dies automatically when main program exits.
            )
            thread.start()
            active_threads.append(thread)

    except KeyboardInterrupt:
        print("\n[Server] Shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
