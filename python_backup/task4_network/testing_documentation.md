# Task 4: Client-Server Networking — Testing Documentation

**Module:** ST5004CEM Operating Systems and Security  
**Task:** Task 4 — Client-Server Application Using Sockets  
**Platform:** Windows / Ubuntu (Python 3)

---

## How to Run

### Server
```
python task4_network/server_v5.py
```
The server listens on `127.0.0.1:5000`. It handles multiple clients concurrently via threading.

### Client
```
python task4_network/client_v5.py <username> <password>
```
Or run without arguments to be prompted for credentials:
```
python task4_network/client_v5.py
```

### Multi-Client Test
Run the server once, then start 2-3 clients in separate terminals:
```
Terminal 1: python task4_network/server_v5.py
Terminal 2: python task4_network/client_v5.py alice password123
Terminal 3: python task4_network/client_v5.py bob bobPass456
Terminal 4: python task4_network/client_v5.py alice wrongpass
```

---

## Protocol Commands

All messages are JSON objects sent over TCP.

### LOGIN
Authenticates the client. Must be sent before any other command.

**Request:**
```json
{
  "command": "LOGIN",
  "username": "alice",
  "password": "password123"
}
```

**Success Response:**
```json
{
  "status": "ok",
  "result": "Login successful"
}
```

**Failure Response:**
```json
{
  "status": "error",
  "error": "Invalid credentials"
}
```

---

### ECHO
Returns the data string unchanged.

**Request:**
```json
{
  "command": "ECHO",
  "data": "Hello, world!"
}
```

**Response:**
```json
{
  "status": "ok",
  "result": "Hello, world!"
}
```

---

### UPPERCASE
Returns the data string converted to uppercase.

**Request:**
```json
{
  "command": "UPPERCASE",
  "data": "hello world"
}
```

**Response:**
```json
{
  "status": "ok",
  "result": "HELLO WORLD"
}
```

---

### REVERSE
Returns the data string reversed.

**Request:**
```json
{
  "command": "REVERSE",
  "data": "hello"
}
```

**Response:**
```json
{
  "status": "ok",
  "result": "olleh"
}
```

---

### Error Responses

**Unknown command:**
```json
{
  "status": "error",
  "error": "Unknown command: 'INVALID'"
}
```

**Missing data field:**
```json
{
  "status": "error",
  "error": "Missing 'data' field"
}
```

**Malformed JSON:**
```json
{
  "status": "error",
  "error": "Invalid JSON format"
}
```

**Not authenticated:**
```json
{
  "status": "error",
  "error": "Not authenticated. Please LOGIN first."
}
```

---

## Test Scenarios Summary

| Stage | Test | Description | Result |
|-------|------|-------------|--------|
| 1 | Basic connection | Server accepts one client connection | PASS |
| 1 | Send/receive message | Client sends text, server echoes it back | PASS |
| 1 | Connection cleanup | Both sockets close cleanly | PASS |
| 2 | JSON protocol | Client sends JSON commands, server responds with JSON | PASS |
| 2 | ECHO command | Server returns data unchanged | PASS |
| 2 | UPPERCASE command | Server returns data in uppercase | PASS |
| 2 | REVERSE command | Server returns data reversed | PASS |
| 2 | Unknown command | Server returns error for unrecognized command | PASS |
| 2 | Missing data field | Server returns error for missing "data" | PASS |
| 2 | Malformed JSON | Server returns error for invalid JSON | PASS |
| 3 | Multiple clients | Server handles 3 clients simultaneously | PASS |
| 3 | Concurrent responses | All clients receive correct responses without interference | PASS |
| 3 | Client disconnect | Server detects disconnection and continues serving others | PASS |
| 4 | Successful login | Client authenticates with correct credentials | PASS |
| 4 | Failed login (wrong password) | Server rejects invalid credentials | PASS |
| 4 | Unauthenticated command | Server rejects commands before LOGIN | PASS |
| 5 | Timeout handling | Silent client is closed after 60s without hanging server | PASS |
| 5 | Abrupt disconnect | Server handles client crash without affecting others | PASS |
| 5 | Graceful shutdown | Server closes cleanly on Ctrl+C without traceback | PASS |

---

## Registered Test Credentials

| Username | Password | Role |
|----------|----------|------|
| alice | password123 | user |
| bob | bobPass456 | user |
| charlie | charlie789 | user |

---

## Error Handling Design

The server (Stage 5) defensively handles:
- **Invalid JSON** — returns error, keeps connection open for more commands.
- **Missing fields** — returns specific error about which field is missing.
- **Unknown commands** — returns error with the unrecognized command name.
- **Authentication bypass** — rejects any non-LOGIN command before successful login.
- **Client timeout** — closes connections silent for 60+ seconds.
- **Abrupt disconnection** — catches ConnectionResetError, BrokenPipeError, etc.
- **Invalid encoding** — catches UnicodeDecodeError for non-UTF-8 data.
- **Unexpected errors** — catch-all exception handler prevents thread/server crash.
- **Graceful shutdown** — Ctrl+C closes the listening socket cleanly.
