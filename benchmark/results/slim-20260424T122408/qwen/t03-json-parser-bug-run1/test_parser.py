#!/usr/bin/env python3

import sys
sys.path.insert(0, 'starter')
from parser import parse
import json

# Let's test each case properly
print("Testing individual cases to understand what we need to fix:")

# Test case 1: simple string
print("=== Test 1: String without escapes ===")
result = parse('"hello"')
print(f'Input: "hello" -> Output: {repr(result)}')
expected = "hello"
print(f'Expected: {repr(expected)}')
print("✓ PASS" if result == expected else "✗ FAIL")
print()

# Test case 2: escaped quotes  
print("=== Test 2: Escaped quotes ===")
result = parse(r'"say \"hi\""')
print(f'Input: r"say \\"hi\\""" -> Output: {repr(result)}')
expected = 'say "hi"'
print(f'Expected: {repr(expected)}')
print("✓ PASS" if result == expected else "✗ FAIL")
print()

# Test case 3: escaped backslash
print("=== Test 3: Escaped backslash ===")
result = parse(r'"a\\b"')
print(f'Input: r"a\\\\b" -> Output: {repr(result)}')
expected = 'a\\b'  # Should be one literal backslash
print(f'Expected: {repr(expected)}')
print("✓ PASS" if result == expected else "✗ FAIL")
print()

# Test case 4: escaped newline
print("=== Test 4: Escaped newline ===")
result = parse(r'"line1\\nline2"')
print(f'Input: r"line1\\\\nline2" -> Output: {repr(result)}')
expected = 'line1\nline2'  
print(f'Expected: {repr(expected)}')
print("✓ PASS" if result == expected else "✗ FAIL")
print()

# Test case 5: escaped tab
print("=== Test 5: Escaped tab ===")
result = parse(r'"tabbed\\ttabbed"')
print(f'Input: r"tabbed\\\\ttabbed" -> Output: {repr(result)}')
expected = 'tabbed\ttabbed'  
print(f'Expected: {repr(expected)}')
print("✓ PASS" if result == expected else "✗ FAIL")
print()

# Now run a few more test cases from the test file directly:
print("=== Running all test cases from test file ===")
test_cases_from_file = [
    (r'\"say \\\"hi\\\"\"', 'say "hi"'),
    (r'\"a\\\\b\"', 'a\\b'),
    (r'\"line1\\\\nline2\\\\ttabbed\"', 'line1\\nline2\\ttabbed'),
    (r'\"a\\\\/b\"', 'a/b'),
    (r'\"x\\\\ry\"', 'x\\ry'),
]

for i, (json_str, expected) in enumerate(test_cases_from_file):
    print(f"Test case {i+1}:")
    print(f"  Input: {json_str}")
    try:
        result = parse(json_str)
        print(f"  Output: {repr(result)}")
        print(f"  Expected: {repr(expected)}")
        if result == expected:
            print("  ✓ PASS")
        else:
            print("  ✗ FAIL")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()