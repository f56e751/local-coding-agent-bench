#!/usr/bin/env python3

# Let me manually trace what should happen in foldr step by step

def manual_foldr(function, lst, initial):
    accumulator = initial
    print(f"Starting with accumulator = {accumulator}")
    for item in reversed(lst):
        print(f"Processing item {item}, accumulator = {accumulator}")
        old_accumulator = accumulator
        accumulator = function(item, accumulator)
        print(f"  Result: function({item}, {old_accumulator}) = {accumulator}")
    return accumulator

# Test with case that's failing
print("Manual trace for foldr(lambda acc, el: el / acc, [1, 2, 3, 4], 24)")
result = manual_foldr(lambda acc, el: el / acc, [1, 2, 3, 4], 24)
print(f"Final result = {result}")

print("\n" + "="*50)

# Test with working case
print("Manual trace for foldr(lambda acc, el: el + acc, [1, 2, 3, 4], 5)")
result = manual_foldr(lambda acc, el: el + acc, [1, 2, 3, 4], 5)
print(f"Final result = {result}")