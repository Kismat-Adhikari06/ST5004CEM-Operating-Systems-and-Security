#!/bin/bash
# Test script for Task 2: Memory Management
# Run from project root: bash tests/test_task2.sh

PASS=0
FAIL=0
BIN="bin"

green() { printf "  \033[32mPASS\033[0m  %s\n" "$1"; ((PASS++)); }
red()   { printf "  \033[31mFAIL\033[0m  %s\n" "$1"; ((FAIL++)); }

echo "============================================"
echo "  Task 2: Memory Management"
echo "============================================"
echo ""

# 1 paging_model
if [ -x "$BIN/paging_model" ]; then
    output=$(printf "4096\n4\n100\n200\n300\nq\n" | "$BIN/paging_model" 2>&1)
    if echo "$output" | grep -q "Paging Model Simulator"; then
        green "paging_model runs"
    else
        red "paging_model missing title"
    fi
    if echo "$output" | grep -q "Page size: 4096"; then
        green "paging_model shows page size"
    else
        red "paging_model missing page size"
    fi
    if echo "$output" | grep -q "Page offset bits:"; then
        green "paging_model shows offset bits"
    else
        red "paging_model missing offset bits"
    fi
    if echo "$output" | grep -q "Frame table:"; then
        green "paging_model shows frame table"
    else
        red "paging_model missing frame table"
    fi
    if echo "$output" | grep -q "Goodbye"; then
        green "paging_model exits gracefully"
    else
        red "paging_model missing goodbye"
    fi
else
    red "paging_model binary not found"
fi

# 2 fifo_replacement
if [ -x "$BIN/fifo_replacement" ]; then
    output=$(printf "3\n" | "$BIN/fifo_replacement" 2>&1)
    if echo "$output" | grep -q "FIFO Page Replacement"; then
        green "fifo_replacement runs"
    else
        red "fifo_replacement missing title"
    fi
    if echo "$output" | grep -q "Hits:"; then
        green "fifo_replacement shows hits"
    else
        red "fifo_replacement missing hits"
    fi
    if echo "$output" | grep -q "Faults:"; then
        green "fifo_replacement shows faults"
    else
        red "fifo_replacement missing faults"
    fi
    hits=$(echo "$output" | grep "Hits:" | grep -oP '\d+')
    faults=$(echo "$output" | grep "Faults:" | grep -oP '\d+')
    if [ -n "$hits" ] && [ -n "$faults" ]; then
        total=$((hits + faults))
        if [ "$total" -eq 12 ]; then
            green "fifo_replacement: $hits hits + $faults faults = 12 total"
        else
            red "fifo_replacement: hits+fauls=$total, expected 12"
        fi
    else
        red "fifo_replacement could not parse hit/fault counts"
    fi
    if echo "$output" | grep -q "Hit ratio:"; then
        green "fifo_replacement shows hit ratio"
    else
        red "fifo_replacement missing hit ratio"
    fi
else
    red "fifo_replacement binary not found"
fi

# 3 lru_replacement
if [ -x "$BIN/lru_replacement" ]; then
    output=$(printf "3\n" | "$BIN/lru_replacement" 2>&1)
    if echo "$output" | grep -q "LRU Page Replacement"; then
        green "lru_replacement runs"
    else
        red "lru_replacement missing title"
    fi
    if echo "$output" | grep -q "Hits:"; then
        green "lru_replacement shows hits"
    else
        red "lru_replacement missing hits"
    fi
    if echo "$output" | grep -q "Faults:"; then
        green "lru_replacement shows faults"
    else
        red "lru_replacement missing faults"
    fi
    hits=$(echo "$output" | grep "Hits:" | grep -oP '\d+')
    faults=$(echo "$output" | grep "Faults:" | grep -oP '\d+')
    if [ -n "$hits" ] && [ -n "$faults" ]; then
        total=$((hits + faults))
        if [ "$total" -eq 12 ]; then
            green "lru_replacement: $hits hits + $faults faults = 12 total"
        else
            red "lru_replacement: hits+fauls=$total, expected 12"
        fi
    else
        red "lru_replacement could not parse hit/fault counts"
    fi
else
    red "lru_replacement binary not found"
fi

# 4 compare_algorithms
if [ -x "$BIN/compare_algorithms" ]; then
    output=$("$BIN/compare_algorithms" 2>&1)
    if echo "$output" | grep -q "Algorithm Comparison"; then
        green "compare_algorithms runs"
    else
        red "compare_algorithms missing title"
    fi
    if echo "$output" | grep -q "FIFO"; then
        green "compare_algorithms shows FIFO results"
    else
        red "compare_algorithms missing FIFO"
    fi
    if echo "$output" | grep -q "LRU"; then
        green "compare_algorithms shows LRU results"
    else
        red "compare_algorithms missing LRU"
    fi
    if echo "$output" | grep -q "Hit Ratio"; then
        green "compare_algorithms shows comparison table"
    else
        red "compare_algorithms missing Hit Ratio column"
    fi
else
    red "compare_algorithms binary not found"
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
echo "============================================"

exit $FAIL
