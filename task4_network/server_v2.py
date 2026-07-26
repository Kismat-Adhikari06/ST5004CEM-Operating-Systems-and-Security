"""
ST5004CEM - Task 4: Networking
Stage 2: Structured Protocol with JSON Messages

This server uses a defined protocol: all messages are JSON objects
with "command" and "data" fields. Supports validation and multiple
commands.
"""

import socket
import json


# --- Why Use a Defined Protocol? ---
#
# Raw text protocols ("just send a string") break down quickly:
#   - How does the server know where one message ends and another begins?
#   - How does it distinguish "ECHO hello" from "hello ECHO"?
#   - What if the message contains special characters or newlines?
#
# A structured protocol (JSON, in this case) solves all of these:
#   - Each message is a complete JSON object (one parseable unit).
#   - Fields have fixed names ("command", "data") so the server
#     knows exactly what each part means.
#   - Responses also follow a structure ("status", "result") so the
#     client can programmatically handle success or failure.
#
# In real applications, this is how HTTP, gRPC, and every network
# API works — defined message formats, not raw strings.
#
# --- Why Validate Client Input? ---
#
# NEVER trust data from the client. The client could:
#   - Send malformed JSON (intentionally or by bug).
#   - Send an unknown command (probing for capabilities).
#   - Omit required fields (testing error handling).
#
# The server must validate EVERYTHING and respond with a clear error
# instead of crashing or executing unintended logic.

HOST = "127.0.0.1"
PORT = 5000


def handle_command(request):
    """
    Parse a JSON request and execute the requested command.

    Returns a JSON response dict with "status" and "result" or "error".
    """
    # Validate: is it valid JSON?
    try:
        data = json.loads(request)
    except json.JSONDecodeError:
        return {"status": "error", "error": "Invalid JSON format"}

    # Validate: does it have a "command" field?
    if "command" not in data:
        return {"status": "error", "error": "Missing 'command' field"}

    # Validate: does it have a "data" field?
    if "data" not in data:
        return {"status": "error", "error": "Missing 'data' field"}

    command = data["command"]
    payload = data["data"]

    # Only accept string data.
    if not isinstance(payload, str):
        return {"status": "error", "error": "'data' field must be a string"}

    # Execute the command.
    if command == "ECHO":
        return {"status": "ok", "result": payload}

    elif command == "UPPERCASE":
        return {"status": "ok", "result": payload.upper()}

    elif command == "REVERSE":
        return {"status": "ok", "result": payload[::-1]}

    else:
        return {"status": "error", "error": f"Unknown command: '{command}'"}


def main():
    print("=== Stage 2: TCP Server (JSON Protocol) ===\n")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server listening on {HOST}:{PORT}...")
    print("Waiting for a client to connect...\n")

    client_socket, client_address = server_socket.accept()
    print(f"Client connected from {client_address}\n")

    # Handle multiple requests from the same client in a loop.
    # recv() returns empty bytes (b"") when the client closes its end,
    # which signals us to stop.
    while True:
        raw_data = client_socket.recv(4096)
        if not raw_data:
            break  # Client disconnected.

        request = raw_data.decode("utf-8")
        print(f"Received: {request}")

        response = handle_command(request)
        response_json = json.dumps(response)
        client_socket.sendall(response_json.encode("utf-8"))
        print(f"Sent: {response_json}\n")

    client_socket.close()
    server_socket.close()
    print("Client disconnected. Server shutting down.")


if __name__ == "__main__":
    main()
