# ST5004CEM Operating Systems and Security - Coursework

A comprehensive C-based implementation covering operating systems concepts including multi-threading, memory management, secure file systems, and network programming.

## Language Requirement

All programs in this project are written in **C (C11 standard)**. The project must be compiled with GCC on a Linux/WSL environment.

## Supported Environment

- **WSL (Windows Subsystem for Linux)** — Ubuntu 20.04 LTS or later
- **Native Linux** — Ubuntu 20.04 LTS or later
- **macOS** — via Homebrew GCC (limited testing)

## Dependencies

Install the required packages with:

```bash
sudo apt update
sudo apt install -y build-essential libssl-dev pkg-config valgrind
```

| Package | Purpose |
|---------|---------|
| `build-essential` | GCC compiler, make, and related tools |
| `libssl-dev` | OpenSSL development libraries (for encryption in Task 3) |
| `pkg-config` | Build system helper for library flags |
| `valgrind` | Memory leak detection (optional, for development) |

## Installation and Compilation

```bash
# Clone or navigate to the project root
cd "Assignment for OS"

# Compile all targets
make

# Or compile specific targets
make bin/process_creation
make bin/secure_file_manager
```

All executables are placed in the `bin/` directory.

### Available Make Targets

| Target | Description |
|--------|-------------|
| `all` / `make` | Compile everything |
| `clean` | Remove all executables and object files |
| `test` | Compile and run all test scripts |
| `sanitize` | Compile with AddressSanitizer and run tests |

## How to Run Each Task

### Task 1: Threading and Process Management

```bash
# Process creation (fork/exec/wait)
bin/process_creation

# Basic threading demo (3 threads)
bin/threading_demo

# Race condition demonstration
bin/race_condition_demo

# Lock fix (mutex) demonstration
bin/lock_fix_demo

# Deadlock detection and prevention
bin/deadlock_demo

# Round-robin CPU scheduler simulation
bin/round_robin_scheduler
```

### Task 2: Memory Management

```bash
# Paging model simulator (interactive)
bin/paging_model

# FIFO page replacement
bin/fifo_replacement

# LRU page replacement
bin/lru_replacement

# FIFO vs LRU algorithm comparison
bin/compare_algorithms
```

### Task 3: Secure File Management System

```bash
# Interactive secure file manager
bin/secure_file_manager
```

Commands available inside the file manager: `register`, `login`, `logout`, `create`, `read`, `write`, `delete`, `list`, `encrypt`, `audit`, `whoami`, `help`, `quit`.

### Task 4: Network Client-Server

```bash
# Start the server (listens on 127.0.0.1:5000)
bin/network_server

# In another terminal, connect a client
bin/network_client <username> <password>
```

Registered users: `alice`/`password123`, `bob`/`bobPass456`, `charlie`/`charlie789`.

## Test Instructions

```bash
# Run all tests
make test

# Run individual test suites
bash tests/test_task1.sh
bash tests/test_task2.sh
bash tests/test_task3.sh
bash tests/test_task4.sh

# Run with AddressSanitizer for memory error detection
make sanitize
```

Test scripts verify:
- Correct output patterns and return codes
- Expected behavior for success and failure cases
- Concurrency correctness where applicable
- Security enforcement (authentication, permissions, encryption)

## Folder Structure

```
Assignment for OS/
├── Makefile                  # Build system
├── README.md                 # This file
├── bin/                      # Compiled executables
├── common/                   # Shared utility code
├── docs/
│   ├── design_decisions.md   # Architecture and design rationale
│   ├── protocol.md           # Network protocol specification
│   ├── security_analysis.md  # Security analysis of the file system
│   └── testing_results.md    # Test results (placeholder)
├── task1_threading/          # Task 1: Threading & Process Management
│   ├── process_creation.c
│   ├── threading_demo.c
│   ├── race_condition_demo.c
│   ├── lock_fix_demo.c
│   ├── deadlock_demo.c
│   └── round_robin_scheduler.c
├── task2_memory/             # Task 2: Memory Management
│   ├── paging_model.c
│   ├── fifo_replacement.c
│   ├── lru_replacement.c
│   ├── compare_algorithms.c
│   ├── memory_simulator.c
│   └── memory_simulator.h
├── python_backup/             # Original Python source files (archived)
├── task3_filesystem/         # Task 3: Secure File Management
│   ├── secure_file_manager.c
│   ├── auth_system.c/h
│   ├── file_operations.c/h
│   ├── permission_system.c/h
│   ├── encryption_system.c/h
│   └── audit_log.c/h
├── task4_network/            # Task 4: Networking
│   ├── server.c
│   ├── client.c
│   └── protocol.c/h
├── tests/
│   ├── test_task1.sh
│   ├── test_task2.sh
│   ├── test_task3.sh
│   └── test_task4.sh
├── vault/                    # File system vault directory
└── audit_log.txt             # Audit log output
```

## Assignment Requirement Mapping

| Assignment Component | Implementation |
|---------------------|----------------|
| Multi-threading (Task 1) | `threading_demo.c` — pthread creation/joining |
| Race conditions (Task 1) | `race_condition_demo.c` vs `lock_fix_demo.c` |
| Deadlocks (Task 1) | `deadlock_demo.c` — circular wait detection and lock ordering fix |
| CPU Scheduling (Task 1) | `round_robin_scheduler.c` — round-robin simulation |
| Process Management (Task 1) | `process_creation.c` — fork/exec/wait |
| Paging (Task 2) | `paging_model.c` — logical-to-physical address translation |
| Page Replacement (Task 2) | FIFO and LRU with hit/fault ratio comparison |
| File Operations (Task 3) | Create, read, write, delete within a secure vault |
| Authentication (Task 3) | Password hashing with salting (SHA-256) |
| Permissions (Task 3) | Unix-style rwx owner/group/others model |
| Encryption (Task 3) | AES-256-CBC via OpenSSL EVP |
| Audit Logging (Task 3) | Append-only audit trail with querying |
| Network Programming (Task 4) | TCP socket server/client with JSON protocol |
| Concurrent Clients (Task 4) | Thread-per-client server architecture |

## Known Limitations

1. **Task 3 user storage**: Users are stored in memory and lost on program restart. A production system would use a database.
2. **Encryption keys**: Keys are generated during runtime and not persisted. The demo encrypts/decrypts in the same session.
3. **Task 4 authentication**: User credentials are hardcoded in the server. A real system would use a database.
4. **Single-threaded file operations**: The file manager does not use file locking for concurrent access.
5. **No TLS**: Network communication is plain TCP. Real applications should use TLS/SSL.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `gcc: command not found` | Install build-essential: `sudo apt install build-essential` |
| `openssl/evp.h: No such file or directory` | Install libssl-dev: `sudo apt install libssl-dev` |
| `pkg-config: command not found` | Install pkg-config: `sudo apt install pkg-config` |
| `fatal error: pthread.h: No such file or directory` | Install glibc: `sudo apt install libc6-dev` |
| `make: not found` | Install build-essential: `sudo apt install build-essential` |
| `AddressSanitizer:DEADLYSIGNAL` | A bug was detected — run with `make sanitize` and fix the reported issue |
