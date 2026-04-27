#!/usr/bin/env python3

import list_ops

# Test foldr specifically 
print("Testing foldr...")
try:
    result = list_ops.foldr(lambda acc, el: el / acc, [1, 2, 3, 4], 24)
    print(f"foldr(lambda acc, el: el / acc, [1, 2, 3, 4], 24) = {result}")
    print("Expected: 9")
except Exception as e:
    print(f"Error in foldr: {e}")

# Test foldl specifically
print("\nTesting foldl...")
try:
    result = list_ops.foldl(lambda acc, el: el / acc, [1, 2, 3, 4], 24)
    print(f"foldl(lambda acc, el: el / acc, [1, 2, 3, 4], 24) = {result}")
    print("Expected: 64")
except Exception as e:
    print(f"Error in foldl: {e}")

# Test a few other functions for sanity
print("\nTesting other functions...")
try:
    result = list_ops.append([1, 2], [3, 4])
    print(f"append([1, 2], [3, 4]) = {result}")
    
    result = list_ops.concat([[1, 2], [3], [], [4, 5, 6]])
    print(f"concat([[1, 2], [3], [], [4, 5, 6]]) = {result}")
    
    result = list_ops.reverse([1, 2, 3, 4])
    print(f"reverse([1, 2, 3, 4]) = {result}")
    
except Exception as e:
    print(f"Error in other functions: {e}")