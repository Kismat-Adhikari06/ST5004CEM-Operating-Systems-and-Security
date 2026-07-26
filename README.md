# ST5004CEM - Operating Systems and Security

Individual coursework for ST5004CEM. Built in Python, runs on Windows and Ubuntu.

---

## Task 1: Threading (`task1_threading/`)

- `threading_demo.py` — Creates 3+ threads, shows them running at the same time
- `race_condition_demo.py` — Shared counter without locks, shows data going wrong
- `lock_fix_demo.py` — Same counter with a lock, shows it works correctly
- `round_robin_scheduler.py` — Simulates a CPU scheduler giving each process a time slice
- `deadlock_demo.py` — Shows deadlock happening, then fixes it with lock ordering

Run any file: `python task1_threading/<filename>.py`

---

## Task 2: Memory Management (`task2_memory/`)

- `paging_model.py` — Basic paging with frames, no replacement yet
- `fifo_replacement.py` — FIFO page replacement (evicts oldest page)
- `lru_replacement.py` — LRU page replacement (evicts least recently used page)
- `compare_algorithms.py` — Runs FIFO vs LRU side by side with different configs

Run any file: `python task2_memory/<filename>.py`

---

## Task 3: File System (`task3_filesystem/`)

- `file_operations.py` — Create, read, write, delete files in a vault folder
- `auth_system.py` — User registration and login with password hashing
- `permission_system.py` — Unix-style rwx permissions (owner/group/others)
- `encryption_system.py` — Encrypt/decrypt files using Fernet (needs `pip install cryptography`)
- `audit_log.py` — Logs every action (login, read, write, denied access, etc.)

Run any file: `python task3_filesystem/<filename>.py`

---

## Task 4: Networking (`task4_network/`)

- `server.py` / `client.py` — Basic client-server, one message
- `server_v2.py` / `client_v2.py` — JSON protocol with commands (ECHO, UPPERCASE, REVERSE)
- `server_v3.py` / `client_v3.py` — Multiple clients at the same time using threads
- `server_v4.py` / `client_v4.py` — Adds login/authentication
- `server_v5.py` — Final version with error handling, timeouts, graceful shutdown
- `testing_documentation.md` — How to run everything and test results

Run server first, then client(s) in separate terminals:
```
python task4_network/server_v5.py
python task4_network/client_v4.py alice password123
```

---

## Requirements

- Python 3
- `cryptography` library (Task 3 encryption only): `pip install cryptography`
