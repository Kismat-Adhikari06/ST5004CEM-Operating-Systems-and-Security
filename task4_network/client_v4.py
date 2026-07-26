"""
ST5004CEM - Task 4: Networking
Stage 4: Client with Authentication

This client logs in before sending commands. Supports both successful
and failed login scenarios via command-line arguments.
"""

import socket
import sys
import json


HOST = "127.0.0.1"
PORT = 5000


def send_request(client_socket, request):
    """Send a JSON request and return the response."""
    client_socket.sendall(json.dumps(request).encode("utf-8"))
    response_raw = client_socket.recv(4096)
    return json.loads(response_raw.decode("utf-8"))


def main():
    # Parse command-line arguments for username/password.
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = input("Username: ").strip()
        password = input("Password: ").strip()

    print(f"\n=== Client: {username} ===\n")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[{username}] Connecting to {HOST}:{PORT}...")
    client_socket.connect((HOST, PORT))
    print(f"[{username}] Connected!\n")

    # --- Step 1: Attempt LOGIN ---
    print(f"[{username}] >>> LOGIN")
    response = send_request(client_socket, {
        "command": "LOGIN",
        "username": username,
        "password": password,
    })
    print(f"[{username}] <<< {json.dumps(response, indent=4)}\n")

    if response.get("status") != "ok":
        print(f"[{username}] Login failed. Cannot send commands.")
        client_socket.close()
        return

    # --- Step 2: Send commands (only if login succeeded) ---
    commands = [
        ("ECHO", f"Hello from {username}"),
        ("UPPERCASE", f"this is {username} testing"),
        ("REVERSE", f"authenticated as {username}"),
    ]

    for command, data in commands:
        print(f"[{username}] >>> {command} \"{data}\"")
        response = send_request(client_socket, {"command": command, "data": data})
        print(f"[{username}] <<< {json.dumps(response)}\n")

    client_socket.close()
    print(f"[{username}] Connection closed.")


if __name__ == "__main__":
    main()
