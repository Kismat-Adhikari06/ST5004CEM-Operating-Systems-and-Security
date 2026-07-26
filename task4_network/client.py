"""
ST5004CEM - Task 4: Networking
Stage 1: Basic TCP Client (Single Message)

This script connects to a TCP server, sends a message, and prints
the response.
"""

import socket


# --- Client Setup (connect) ---
#
# Unlike the server (bind -> listen -> accept), the client just calls
# connect() with the server's address. The OS handles the TCP
# three-way handshake automatically:
#   1. Client sends SYN (synchronize) to the server.
#   2. Server replies with SYN-ACK (acknowledge).
#   3. Client sends ACK — connection established.
#
# After connect() returns, both sides can send/receive data.

HOST = "127.0.0.1"  # Server address (must match server.py).
PORT = 5000          # Server port (must match server.py).


def main():
    print("=== Stage 1: TCP Client ===\n")

    # Create a TCP socket.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server.
    print(f"Connecting to {HOST}:{PORT}...")
    client_socket.connect((HOST, PORT))
    print("Connected!\n")

    # Send a message to the server.
    message = "Hello from client"
    client_socket.sendall(message.encode("utf-8"))
    print(f"Sent: \"{message}\"")

    # Wait for and receive the server's response.
    data = client_socket.recv(1024)
    response = data.decode("utf-8")
    print(f"Received: \"{response}\"")

    # Close the socket.
    client_socket.close()
    print("\nConnection closed.")


if __name__ == "__main__":
    main()
