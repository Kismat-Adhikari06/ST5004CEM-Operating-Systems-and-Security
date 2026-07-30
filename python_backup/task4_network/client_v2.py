"""
ST5004CEM - Task 4: Networking
Stage 2: Structured Protocol with JSON Messages

This client sends JSON-formatted commands to the server and prints
structured responses. Tests multiple commands including error cases.
"""

import socket
import json


HOST = "127.0.0.1"
PORT = 5000


def send_request(client_socket, command, data):
    """
    Send a JSON command to the server and return the response.

    Args:
        client_socket: connected TCP socket.
        command: command string (ECHO, UPPERCASE, REVERSE).
        data: string payload for the command.

    Returns:
        Parsed JSON response dict.
    """
    request = {"command": command, "data": data}
    request_json = json.dumps(request)

    client_socket.sendall(request_json.encode("utf-8"))

    response_raw = client_socket.recv(4096)
    return json.loads(response_raw.decode("utf-8"))


def main():
    print("=== Stage 2: TCP Client (JSON Protocol) ===\n")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to {HOST}:{PORT}...")
    client_socket.connect((HOST, PORT))
    print("Connected!\n")

    # --- Send multiple commands to the server ---
    commands = [
        ("ECHO", "Hello from client"),
        ("UPPERCASE", "this should be uppercase"),
        ("REVERSE", "emoclew ot tsuj"),
        ("ECHO", "testing validation"),
    ]

    for command, data in commands:
        print(f">>> Sending: {command} \"{data}\"")
        response = send_request(client_socket, command, data)
        print(f"    Response: {json.dumps(response, indent=6)}\n")

    # --- Test error handling: unknown command ---
    print(">>> Sending: INVALID \"this command does not exist\"")
    response = send_request(client_socket, "INVALID", "test")
    print(f"    Response: {json.dumps(response, indent=6)}\n")

    # --- Test error handling: missing data field ---
    print(">>> Sending: ECHO with missing data field")
    bad_request = {"command": "ECHO"}  # No "data" field.
    client_socket.sendall(json.dumps(bad_request).encode("utf-8"))
    response_raw = client_socket.recv(4096)
    response = json.loads(response_raw.decode("utf-8"))
    print(f"    Response: {json.dumps(response, indent=6)}\n")

    # --- Test error handling: malformed JSON ---
    print(">>> Sending: malformed JSON (not valid)")
    client_socket.sendall("this is not json".encode("utf-8"))
    response_raw = client_socket.recv(4096)
    response = json.loads(response_raw.decode("utf-8"))
    print(f"    Response: {json.dumps(response, indent=6)}\n")

    client_socket.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()
