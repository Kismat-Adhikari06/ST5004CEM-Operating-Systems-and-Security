"""
ST5004CEM - Task 4: Networking
Stage 1: Basic TCP Server (Single Client)

This script runs a simple TCP server that accepts one connection,
receives a message, sends a response, then closes.
"""

import socket


# --- What is a Socket? ---
#
# A socket is one endpoint of a communication channel between two
# processes. Think of it like a phone: one process "dials" (connects)
# and the other "rings" (listens/accepts). Once connected, both sides
# can send and receive data.
#
# TCP sockets (used here) guarantee:
#   - Data arrives in order.
#   - Data is not corrupted (checksums verify integrity).
#   - Lost packets are automatically retransmitted.
#
# --- Server Setup Sequence (bind -> listen -> accept) ---
#
# 1. bind():    "Reserve" a specific address (IP + port) so other
#               processes know where to reach this server.
# 2. listen():  Tell the OS to start listening for incoming connection
#               requests on that address. The OS maintains a backlog
#               queue of pending connections.
# 3. accept():  Wait (block) until a client connects. When one does,
#               return a NEW socket dedicated to that client. The
#               original listening socket continues to accept more
#               clients (used in Stage 3 for concurrency).
#
# --- Why is this IPC? ---
#
# Inter-Process Communication (IPC) means any way processes exchange
# data. Sockets are IPC because even when both processes run on the
# same machine (localhost), they are separate processes with their
# own memory — the only way to share data is through the OS network
# stack. Sockets also work across machines, which is why they're the
# foundation of all network communication.

HOST = "127.0.0.1"  # localhost — same machine as the client.
PORT = 5000          # Arbitrary port above 1024 (unprivileged).


def main():
    print("=== Stage 1: TCP Server ===\n")

    # Create a TCP socket (IPv4 + stream transport).
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # SO_REUSEADDR allows rebinding to the same port immediately after
    # the server stops, without waiting for the OS to release it.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to the address and start listening.
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)  # backlog of 1 — we only expect one client.
    print(f"Server listening on {HOST}:{PORT}...")
    print("Waiting for a client to connect...\n")

    # accept() blocks until a client connects.
    # Returns a new socket (client_socket) specific to this client,
    # and the client's address (ip, port).
    client_socket, client_address = server_socket.accept()
    print(f"Client connected from {client_address}")

    # Receive data from the client (up to 1024 bytes).
    data = client_socket.recv(1024)
    message = data.decode("utf-8")
    print(f"Received: \"{message}\"")

    # Send a response back to the client.
    response = f"Message received: {message}"
    client_socket.sendall(response.encode("utf-8"))
    print(f"Sent: \"{response}\"")

    # Close both sockets to clean up.
    client_socket.close()
    server_socket.close()
    print("\nConnection closed. Server shutting down.")


if __name__ == "__main__":
    main()
