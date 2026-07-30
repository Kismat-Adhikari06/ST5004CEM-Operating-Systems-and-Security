# Changelog — Python to C Conversion

## Overview

Converted the entire ST5004CEM Operating Systems coursework from Python to C (C11 standard). All 27 Python files were replaced with C implementations and archived to `python_backup/`.

---

## Files Created

### Task 1 — Threading & Process Management (6 files)

| File | Description |
|------|-------------|
| `task1_threading/process_creation.c` | fork/exec/wait process creation demo |
| `task1_threading/threading_demo.c` | 3-thread pthread demo (A, B, C) |
| `task1_threading/race_condition_demo.c` | Race condition without mutex |
| `task1_threading/lock_fix_demo.c` | Race condition fixed with mutex |
| `task1_threading/deadlock_demo.c` | Deadlock detection + lock ordering fix |
| `task1_threading/round_robin_scheduler.c` | Round-robin CPU scheduler simulation |

### Task 2 — Memory Management (6 files)

| File | Description |
|------|-------------|
| `task2_memory/memory_simulator.h` | Shared page table/frame data structures |
| `task2_memory/memory_simulator.c` | Simulation engine (reference string, page table) |
| `task2_memory/paging_model.c` | Logical-to-physical address translation |
| `task2_memory/fifo_replacement.c` | FIFO page replacement simulation |
| `task2_memory/lru_replacement.c` | LRU page replacement simulation |
| `task2_memory/compare_algorithms.c` | Side-by-side FIFO vs LRU comparison |

### Task 3 — Secure File Management System (11 files)

| File | Description |
|------|-------------|
| `task3_filesystem/auth_system.h` / `.c` | User registration/login with SHA-256 password hashing |
| `task3_filesystem/file_operations.h` / `.c` | Vault file create/read/write/delete |
| `task3_filesystem/permission_system.h` / `.c` | Unix-style rwx owner/group/others permissions |
| `task3_filesystem/encryption_system.h` / `.c` | AES-256-GCM encryption via OpenSSL EVP |
| `task3_filesystem/audit_log.h` / `.c` | Append-only audit trail with querying |
| `task3_filesystem/secure_file_manager.c` | Interactive CLI integrating all subsystems |

### Task 4 — Network Client-Server (4 files)

| File | Description |
|------|-------------|
| `task4_network/protocol.h` / `.c` | JSON-style protocol encoding/decoding |
| `task4_network/server.c` | TCP server (thread-per-client, SHA256 auth) |
| `task4_network/client.c` | Interactive TCP client (ECHO/UPPERCASE/REVERSE) |

### Shared Infrastructure

| File | Description |
|------|-------------|
| `common/common.h` / `.c` | Utility functions (hex conversion, string trim, validation) |
| `Makefile` | Build system with all, clean, test, sanitize targets |
| `README.md` | Full project documentation |
| `docs/design_decisions.md` | Architecture and design rationale |
| `docs/protocol.md` | Network protocol specification |
| `docs/security_analysis.md` | Security analysis of the file system |
| `docs/testing_results.md` | Test results documentation |
| `tests/test_task1.sh` | Task 1 test script |
| `tests/test_task2.sh` | Task 2 test script |
| `tests/test_task3.sh` | Task 3 test script |
| `tests/test_task4.sh` | Task 4 test script |

---

## Files Modified

| File | Change |
|------|--------|
| `README.md` | Rewrote entirely for C project; added build/test instructions, dependency list, folder structure, and troubleshooting |
| `Makefile` | Initial build rules; later updated to auto-detect MinGW-Windows for `-static` linking, added `dirs` target |
| `docs/testing_results.md` | Changed from placeholder to documented actual results (9 verified, 4 pending Linux) |

---

## Bug Fixes (during development)

| File | Bug | Fix |
|------|-----|-----|
| `task2_memory/paging_model.c` | Missing `#include "memory_simulator.h"` | Added include directive |
| `task2_memory/compare_algorithms.c` | Called `run_test()` instead of `run_both()`; label printed "FIFO" for both | Fixed function call and labels |
| `Makefile` | `network_server` missing `$(LIBS)` for `-lcrypto` (SHA256) | Added `$(LIBS)` to link rule |

---

## Compilation Results (MinGW-w64 on Windows)

| Program | Compiled | Tested | Notes |
|---------|----------|--------|-------|
| `threading_demo` | ✅ | ✅ | 3 threads started correctly |
| `race_condition_demo` | ✅ | ✅ | Counter ~1000 (race confirmed) |
| `lock_fix_demo` | ✅ | ✅ | Counter = 3000 (mutex works) |
| `deadlock_demo` | ✅ | ✅ | Deadlock detected in A; B works |
| `round_robin_scheduler` | ✅ | ✅ | Avg wait 15.20 (correct) |
| `paging_model` | ✅ | ✅ | Translates addresses correctly |
| `fifo_replacement` | ✅ | ✅ | Runs correctly |
| `lru_replacement` | ✅ | ✅ | Runs correctly |
| `compare_algorithms` | ✅ | ✅ | FIFO vs LRU comparison correct |
| `process_creation` | ❌ | — | Needs `fork()` / `sys/wait.h` (WSL/Linux) |
| `secure_file_manager` | ❌ | — | Needs OpenSSL dev headers (WSL/Linux) |
| `network_server` | ❌ | — | Needs `arpa/inet.h`, `netdb.h` (WSL/Linux) |
| `network_client` | ❌ | — | Needs `arpa/inet.h`, `netdb.h` (WSL/Linux) |

---

## Files Archived (Python originals moved to `python_backup/`)

### task1_threading (6 files)
`deadlock_demo.py`, `lock_fix_demo.py`, `main.py`, `race_condition_demo.py`, `round_robin_scheduler.py`, `threading_demo.py`

### task2_memory (5 files)
`compare_algorithms.py`, `fifo_replacement.py`, `lru_replacement.py`, `main.py`, `paging_model.py`

### task3_filesystem (6 files)
`audit_log.py`, `auth_system.py`, `encryption_system.py`, `file_operations.py`, `main.py`, `permission_system.py`

### task4_network (9 files)
`client.py`, `client_v2.py`, `client_v3.py`, `client_v4.py`, `main.py`, `server.py`, `server_v2.py`, `server_v3.py`, `server_v4.py`, `server_v5.py`, `testing_documentation.md`

---

## Remaining Work

1. **Compile on Linux/WSL** — clone repo into WSL, run `make` to compile all 13 programs
2. **Run full test suite** — `make test` and `make sanitize`
3. **Delete `python_backup/`** — only after confirming C programs work correctly on Linux
4. **Fix any Linux-specific issues** — path separators, valgrind warnings, etc.

## How to Build & Test on Linux/WSL

```bash
sudo apt update && sudo apt install -y build-essential libssl-dev pkg-config valgrind
make clean && make
make test
make sanitize
```
