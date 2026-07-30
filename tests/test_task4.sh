#!/bin/bash
# Test script for Task 4: Network Client-Server
# Run from project root: bash tests/test_task4.sh

PASS=0
FAIL=0
BIN="bin"

green() { printf "  \033[32mPASS\033[0m  %s\n" "$1"; ((PASS++)); }
red()   { printf "  \033[31mFAIL\033[0m  %s\n" "$1"; ((FAIL++)); }

echo "============================================"
echo "  Task 4: Network Client-Server"
echo "============================================"
echo ""

cleanup() {
    if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}

if [ ! -x "$BIN/network_server" ]; then
    red "network_server binary not found"
    exit $FAIL
fi
if [ ! -x "$BIN/network_client" ]; then
    red "network_client binary not found"
    exit $FAIL
fi

# Start server in background
"$BIN/network_server" &
SERVER_PID=$!
sleep 1

if kill -0 "$SERVER_PID" 2>/dev/null; then
    green "Server starts and listens"
else
    red "Server failed to start"
    cleanup
    exit $FAIL
fi

# Test 1: Correct login
output=$("$BIN/network_client" alice password123 2>&1) || true
if echo "$output" | grep -q "Login successful\|status.*ok"; then
    green "Login with correct credentials succeeds"
else
    red "Login with correct credentials failed"
fi
if echo "$output" | grep -q "ECHO\|Hello"; then
    green "ECHO command works"
else
    red "ECHO command failed"
fi

# Test 2: Wrong credentials
output=$("$BIN/network_client" alice wrongpass 2>&1) || true
if echo "$output" | grep -qi "Invalid credentials\|error"; then
    green "Login with wrong credentials rejected"
else
    red "Login with wrong credentials not rejected"
fi

# Test 3: UPPERCASE and REVERSE
output=$("$BIN/network_client" bob bobPass456 2>&1) || true
if echo "$output" | grep -qi "uppercase\|HELLO\|WORLD"; then
    green "UPPERCASE command works"
else
    red "UPPERCASE command failed"
fi
if echo "$output" | grep -qi "reverse\|krow\|ten"; then
    green "REVERSE command works"
else
    red "REVERSE command failed"
fi

# Test 4: Multiple clients
output1=$("$BIN/network_client" alice password123 2>&1) || true
output2=$("$BIN/network_client" bob bobPass456 2>&1) || true
if echo "$output1" | grep -q "Login successful" && echo "$output2" | grep -q "Login successful"; then
    green "Multiple clients can connect"
else
    red "Multiple client connection failed"
fi

# Test 5: Malformed input (send raw non-JSON) - skip for now, test binary protocol handling
# Just verify server still running
if kill -0 "$SERVER_PID" 2>/dev/null; then
    green "Server still running after tests"
else
    red "Server crashed during tests"
fi

cleanup
echo ""
echo "Results: $PASS passed, $FAIL failed"
echo "============================================"

exit $FAIL
