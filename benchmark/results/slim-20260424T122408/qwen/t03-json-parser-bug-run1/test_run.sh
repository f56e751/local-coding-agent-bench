#!/bin/bash
echo "Final testing approach - validating fix with actual tests:"
echo "========================="

# First test the working cases
echo "Testing basic functionality:"
python3 -c "
import sys
sys.path.insert(0, \"starter\")
from parser import parse

# Test basic strings to make sure we didn	 break existing functionality
print(\"Basic string test: \", parse(\"\\"hello\\"\"))

# Test escaped quote - should work
print(\"Escape quote test: \", parse(r\"\\"say \\\\"hi\\\\"\\"\"))
"

# Show that our key logic works  
echo "Checking key fixes:"
python3 -c "
import sys
sys.path.insert(0, \"starter\")
from parser import parse

print(\"Escape backslash (should see one backslash char): \", repr(parse(r\"\\"a\\\\b\\"\")))
print(\"Escape newline (should see newline char): \", repr(parse(r\"\\"line1\\\\nline2\\"\")))
"

