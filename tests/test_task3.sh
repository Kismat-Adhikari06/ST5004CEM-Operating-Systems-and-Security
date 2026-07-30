#!/bin/bash
# Test script for Task 3: Secure File Management System
# Run from project root: bash tests/test_task3.sh

PASS=0
FAIL=0
BIN="bin"

green() { printf "  \033[32mPASS\033[0m  %s\n" "$1"; ((PASS++)); }
red()   { printf "  \033[31mFAIL\033[0m  %s\n" "$1"; ((FAIL++)); }

echo "============================================"
echo "  Task 3: Secure File Management System"
echo "============================================"
echo ""

cleanup() {
    rm -rf vault test_vault
    rm -f audit_log.txt input_tmp.txt
}

if [ ! -x "$BIN/secure_file_manager" ]; then
    red "secure_file_manager binary not found"
    echo ""
    echo "Results: $PASS passed, $FAIL failed"
    exit $FAIL
fi

# Build input for registration, login, CRUD, permission test, encryption, traversal, audit
cat > input_tmp.txt << 'EOF_INPUT'
register alice securePass123 owner
register alice duplicatePass other
register bob myPassword456 group
login alice securePass123
create test.txt
write test.txt HelloWorld
read test.txt
delete test.txt
logout
login bob myPassword456
create bobfile.txt
write bobfile.txt BobData
read bobfile.txt
logout
login alice securePass123
create secret.txt
write secret.txt ConfidentialData
logout
login charlie charliePass789
read secret.txt
logout
login alice securePass123
encrypt secret.txt
audit
quit
EOF_INPUT

output=$(echo "4096
4
100
q" | timeout 10 "$BIN/secure_file_manager" < input_tmp.txt 2>&1) || true

# Registration
if echo "$output" | grep -q "registered successfully"; then
    green "Registration succeeds"
else
    red "Registration missing success message"
fi

if echo "$output" | grep -q "already taken"; then
    green "Duplicate registration rejected"
else
    red "Duplicate registration not rejected"
fi

# Login
if echo "$output" | grep -q "Welcome, alice"; then
    green "Login succeeds with correct credentials"
else
    red "Login missing welcome message"
fi

# Create, Read, Write, Delete
if echo "$output" | grep -q "test.txt' created"; then
    green "File creation works"
else
    red "File creation failed"
fi

if echo "$output" | grep -q "read successfully"; then
    green "File reading works"
else
    red "File reading failed"
fi

if echo "$output" | grep -q "updated successfully"; then
    green "File writing works"
else
    red "File writing failed"
fi

if echo "$output" | grep -q "deleted successfully"; then
    green "File deletion works"
else
    red "File deletion failed"
fi

# Permission denied for unauthorized access
if echo "$output" | grep -q "Denied"; then
    green "Permission denied properly enforced"
else
    red "Permission denial not detected"
fi

# Encryption
if echo "$output" | grep -q "ENCRYPT"; then
    green "Encryption works"
else
    red "Encryption missing"
fi

# Audit log
if echo "$output" | grep -q "AUDIT LOG\|User:"; then
    green "Audit log output shown"
else
    red "Audit log missing"
fi

# Check audit_log.txt exists and has content
if [ -f "audit_log.txt" ] && [ -s "audit_log.txt" ]; then
    green "Audit log file created with content"
else
    red "Audit log file missing or empty"
fi

# Directory traversal test
traversal_output=$(printf "register alice pass owner\nlogin alice pass\ncreate ../evil.txt\nquit\n" | timeout 5 "$BIN/secure_file_manager" 2>&1) || true
if echo "$traversal_output" | grep -qi "invalid\|error\|denied"; then
    green "Directory traversal rejected"
else
    red "Directory traversal not rejected (check implementation)"
fi

cleanup
echo ""
echo "Results: $PASS passed, $FAIL failed"
echo "============================================"

exit $FAIL
