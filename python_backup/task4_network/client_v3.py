"""
ST5004CEM - Task 4: Networking
Stage 3: Multi-Client Client (Threaded Server)

Run multiple copies of this script simultaneously to test the
multi-client server. Each client gets a unique name for identification.
"""

import socket
import sys
import json


HOST = "127.0.0.1"
PORT = 5000


def send_request(client_socket, command, data):
    """Send a JSON command and return the response."""
    request = {"command": command, "data": data}
    client_socket.sendall(json.dumps(request).encode("utf-8"))
    response_raw = client_socket.recv(4096)
    return json.loads(response_raw.decode("utf-8"))


def main():
    # Get client name from command-line argument, or prompt for it.
    if len(sys.argv) > 1:
        client_name = sys.argv[1]
    else:
        client_name = input("Enter your client name: ").strip()
        if not client_name:
            client_name = "anonymous"

    print(f"\n=== Client: {client_name} ===\n")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[{client_name}] Connecting to {HOST}:{PORT}...")
    client_socket.connect((HOST, PORT))
    print(f"[{client_name}] Connected!\n")

    # Send a few commands to demonstrate concurrent handling.
    commands = [
        ("ECHO", f"Hello from {client_name}"),
        ("UPPERCASE", f"this is {client_name} testing uppercase"),
        ("REVERSE", f"{client_name} says hello"),
    ]

    for command, data in commands:
        print(f"[{client_name}] >>> {command} \"{data}\"")
        response = send_request(client_socket, command, data)
        print(f"[{client_name}] <<< {json.dumps(response)}\n")

    # Test an error case.
    print(f"[{client_name}] >>> INVALID \"probing\"")
    response = send_request(client_socket, "INVALID", "probing")
    print(f"[{client_name}] <<< {json.dumps(response)}\n")

    client_socket.close()
    print(f"[{client_name}] Connection closed.")


if __name__ == "__main__":
    main()
