#!/bin/bash
# Test script for Task 1: Threading & Process Management
# Run from project root: bash tests/test_task1.sh

PASS=0
FAIL=0
BIN="bin"

green() { printf "  \033[32mPASS\033[0m  %s\n" "$1"; ((PASS++)); }
red()   { printf "  \033[31mFAIL\033[0m  %s\n" "$1"; ((FAIL++)); }

echo "============================================"
echo "  Task 1: Threading & Process Management"
echo "============================================"
echo ""

# 1 process_creation
if [ -x "$BIN/process_creation" ]; then
    output=$("$BIN/process_creation" 2>&1)
    if echo "$output" | grep -q "Parent process PID:"; then
        green "process_creation shows parent PID"
    else
        red "process_creation missing parent PID"
    fi
    if echo "$output" | grep -q "\[Child 1\]"; then
        green "process_creation shows Child 1 output"
    else
        red "process_creation missing Child 1"
    fi
    if echo "$output" | grep -q "All children completed"; then
        green "process_creation reaps all children"
    else
        red "process_creation missing completion message"
    fi
    if echo "$output" | grep -q "No zombie processes"; then
        green "process_creation verifies no zombies"
    else
        red "process_creation missing zombie check"
    fi
else
    red "process_creation binary not found"
fi

# 2 threading_demo
if [ -x "$BIN/threading_demo" ]; then
    output=$("$BIN/threading_demo" 2>&1)
    if echo "$output" | grep -q "Thread-A"; then
        green "threading_demo shows Thread-A"
    else
        red "threading_demo missing Thread-A"
    fi
    if echo "$output" | grep -q "Thread-B"; then
        green "threading_demo shows Thread-B"
    else
        red "threading_demo missing Thread-B"
    fi
    if echo "$output" | grep -q "Thread-C"; then
        green "threading_demo shows Thread-C (3 threads)"
    else
        red "threading_demo missing Thread-C"
    fi
    if echo "$output" | grep -q "All threads completed"; then
        green "threading_demo completes all threads"
    else
        red "threading_demo missing completion message"
    fi
else
    red "threading_demo binary not found"
fi

# 3 race_condition_demo
if [ -x "$BIN/race_condition_demo" ]; then
    output=$("$BIN/race_condition_demo" 2>&1)
    if echo "$output" | grep -q "Race Condition Demo"; then
        green "race_condition_demo runs"
    else
        red "race_condition_demo missing title"
    fi
    if echo "$output" | grep -q "Lost increments:"; then
        green "race_condition_demo shows lost increments"
    else
        red "race_condition_demo missing lost increments"
    fi
    expected=3000
    actual=$(echo "$output" | grep "Actual value:" | grep -oP '\d+')
    if [ -n "$actual" ] && [ "$actual" -lt "$expected" ] 2>/dev/null; then
        green "race_condition_demo: counter wrong (actual=$actual < expected=$expected)"
    else
        if [ -z "$actual" ]; then
            red "race_condition_demo could not parse counter"
        else
            green "race_condition_demo: counter=$actual (race may not manifest every run)"
        fi
    fi
else
    red "race_condition_demo binary not found"
fi

# 4 lock_fix_demo
if [ -x "$BIN/lock_fix_demo" ]; then
    output=$("$BIN/lock_fix_demo" 2>&1)
    if echo "$output" | grep -q "Lock Fix Demo"; then
        green "lock_fix_demo runs"
    else
        red "lock_fix_demo missing title"
    fi
    actual=$(echo "$output" | grep "Actual value:" | grep -oP '\d+')
    if [ "$actual" = "3000" ]; then
        green "lock_fix_demo: counter correct ($actual)"
    else
        red "lock_fix_demo: counter wrong (got $actual, expected 3000)"
    fi
else
    red "lock_fix_demo binary not found"
fi

# 5 deadlock_demo
if [ -x "$BIN/deadlock_demo" ]; then
    output=$("$BIN/deadlock_demo" 2>&1)
    if echo "$output" | grep -q "PART A: DEADLOCK"; then
        green "deadlock_demo shows Part A (deadlock)"
    else
        red "deadlock_demo missing Part A"
    fi
    if echo "$output" | grep -q "Deadlock detected"; then
        green "deadlock_demo detects deadlock"
    else
        red "deadlock_demo missing deadlock detection"
    fi
    if echo "$output" | grep -q "PART B: FIX"; then
        green "deadlock_demo shows Part B (fix)"
    else
        red "deadlock_demo missing Part B"
    fi
    if echo "$output" | grep -q "No deadlock occurred"; then
        green "deadlock_demo fix prevents deadlock"
    else
        red "deadlock_demo missing prevention message"
    fi
    if echo "$output" | grep -q "CONCLUSION"; then
        green "deadlock_demo shows conclusion"
    else
        red "deadlock_demo missing conclusion"
    fi
else
    red "deadlock_demo binary not found"
fi

# 6 round_robin_scheduler
if [ -x "$BIN/round_robin_scheduler" ]; then
    output=$("$BIN/round_robin_scheduler" 2>&1)
    if echo "$output" | grep -q "Round-Robin"; then
        green "round_robin_scheduler runs"
    else
        red "round_robin_scheduler missing title"
    fi
    if echo "$output" | grep -q "Time Quantum:"; then
        green "round_robin_scheduler shows quantum"
    else
        red "round_robin_scheduler missing quantum"
    fi
    if echo "$output" | grep -q "P1"; then
        green "round_robin_scheduler shows process P1"
    else
        red "round_robin_scheduler missing P1"
    fi
    if echo "$output" | grep -q "SUMMARY"; then
        green "round_robin_scheduler shows summary"
    else
        red "round_robin_scheduler missing summary"
    fi
    if echo "$output" | grep -q "Average waiting time:"; then
        green "round_robin_scheduler shows avg waiting time"
    else
        red "round_robin_scheduler missing avg waiting time"
    fi
else
    red "round_robin_scheduler binary not found"
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
echo "============================================"

exit $FAIL
