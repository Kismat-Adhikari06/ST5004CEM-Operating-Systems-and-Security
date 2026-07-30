CC       = gcc
CFLAGS   = -std=c11 -Wall -Wextra -Wpedantic -D_POSIX_C_SOURCE=200809L
LDFLAGS  = -pthread
LIBS     = -lcrypto

# Detect Windows/MinGW for static linking
UNAME_S := $(shell uname -s 2>/dev/null || echo "Unknown")
ifneq (,$(findstring MINGW,$(UNAME_S)))
    CFLAGS += -static
    LDFLAGS += -static
endif

PKG_OPENSSL := $(shell pkg-config --cflags --libs libssl libcrypto 2>/dev/null || echo "-lcrypto")

SRC_T1   = task1_threading
SRC_T2   = task2_memory
SRC_T3   = task3_filesystem
SRC_T4   = task4_network
BIN_DIR  = bin

T1_EXES  = process_creation threading_demo race_condition_demo lock_fix_demo \
           deadlock_demo round_robin_scheduler
T2_EXES  = paging_model fifo_replacement lru_replacement compare_algorithms
T3_EXES  = secure_file_manager
T4_EXES  = network_server network_client

ALL_EXES = $(addprefix $(BIN_DIR)/,$(T1_EXES) $(T2_EXES) $(T3_EXES) $(T4_EXES))

.PHONY: all clean test sanitize dirs

all: dirs $(ALL_EXES)

dirs:
	mkdir -p $(BIN_DIR) vault output_logs

# Task 1 - Threading
$(BIN_DIR)/process_creation: $(SRC_T1)/process_creation.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/threading_demo: $(SRC_T1)/threading_demo.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/race_condition_demo: $(SRC_T1)/race_condition_demo.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/lock_fix_demo: $(SRC_T1)/lock_fix_demo.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/deadlock_demo: $(SRC_T1)/deadlock_demo.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/round_robin_scheduler: $(SRC_T1)/round_robin_scheduler.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# Task 2 - Memory Management
$(BIN_DIR)/paging_model: $(SRC_T2)/paging_model.c $(SRC_T2)/memory_simulator.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/fifo_replacement: $(SRC_T2)/fifo_replacement.c $(SRC_T2)/memory_simulator.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/lru_replacement: $(SRC_T2)/lru_replacement.c $(SRC_T2)/memory_simulator.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN_DIR)/compare_algorithms: $(SRC_T2)/compare_algorithms.c $(SRC_T2)/memory_simulator.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# Task 3 - Secure File System
T3_SRCS  = $(wildcard $(SRC_T3)/*.c)
$(BIN_DIR)/secure_file_manager: $(T3_SRCS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS) $(PKG_OPENSSL) $(LIBS)

# Task 4 - Networking
$(BIN_DIR)/network_server: $(SRC_T4)/server.c $(SRC_T4)/protocol.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS) $(LIBS)

$(BIN_DIR)/network_client: $(SRC_T4)/client.c $(SRC_T4)/protocol.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -rf $(BIN_DIR) *.o *.obj
	rm -f audit_log.txt
	rm -rf vault/*.enc vault/*.enc.key vault/*.dec

test: all
	@echo "=== Running Task 1 Tests ==="
	@bash tests/test_task1.sh
	@echo ""
	@echo "=== Running Task 2 Tests ==="
	@bash tests/test_task2.sh
	@echo ""
	@echo "=== Running Task 3 Tests ==="
	@bash tests/test_task3.sh
	@echo ""
	@echo "=== Running Task 4 Tests ==="
	@bash tests/test_task4.sh
	@echo ""
	@echo "=== All Tests Complete ==="

sanitize: CFLAGS += -fsanitize=address -g -fno-omit-frame-pointer
sanitize: LDFLAGS += -fsanitize=address
sanitize: clean all
	@echo "=== Running Tests with Address Sanitizer ==="
	@bash tests/test_task1.sh
	@bash tests/test_task2.sh
	@echo "=== Sanitizer Tests Complete ==="
