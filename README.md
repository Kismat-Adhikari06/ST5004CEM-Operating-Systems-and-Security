# ST5004CEM Operating Systems and Security — Coursework

C (C11) coursework covering multi-threading, memory management, secure file systems, and network programming.

## Quick Start (Linux/WSL)

```bash
sudo apt update && sudo apt install -y build-essential libssl-dev pkg-config
make
```

All executables go in `bin/`.

## What's Here

| Task | Files | What It Does |
|------|-------|-------------|
| **1 — Threading** | 6 C files | pthreads, race condition vs mutex fix, deadlock detection, round-robin scheduler, fork demo |
| **2 — Memory** | 6 C/H files | Paging address translation, FIFO, LRU, algorithm comparison |
| **3 — Secure FS** | 11 C/H files | Auth (SHA-256), file ops with Unix permissions, AES-256-GCM encryption, audit logging |
| **4 — Network** | 4 C/H files | TCP server (thread-per-client), JSON protocol client, SHA-256 auth |

## How to Run

```bash
# Task 1
./bin/threading_demo          # 3 threads
./bin/race_condition_demo     # race (counter < 3000)
./bin/lock_fix_demo           # mutex fix (counter = 3000)
./bin/deadlock_demo           # deadlock detection + prevention
./bin/round_robin_scheduler   # CPU scheduling sim
./bin/process_creation        # fork/exec/wait

# Task 2
./bin/paging_model            # address translation
./bin/fifo_replacement        # FIFO page replacement
./bin/lru_replacement         # LRU page replacement
./bin/compare_algorithms      # FIFO vs LRU comparison

# Task 3
./bin/secure_file_manager     # interactive file manager

# Task 4 (run in two terminals)
./bin/network_server          # start server on :5000
./bin/network_client alice password123   # connect client
```

## Testing

```bash
make test          # run all test scripts
make sanitize      # run with AddressSanitizer
```

## Folder Layout

```
├── Makefile
├── README.md
├── common/              # shared utilities
├── task1_threading/     # 6 source files
├── task2_memory/        # 5 source + 1 header
├── task3_filesystem/    # 11 C/H files
├── task4_network/       # 3 source + 1 header
├── tests/               # 4 shell test scripts
├── vault/               # seed data files
└── bin/                 # compiled executables
```
