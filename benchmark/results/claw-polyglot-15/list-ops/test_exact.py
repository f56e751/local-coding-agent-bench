#!/usr/bin/env python3

# Direct code copy to see if the implementation is actually working as intended
def foldr(function, list, initial):
    """Fold (reduce) each item into the accumulator from the right."""
    accumulator = initial
    # Process list in reverse order
    for item in reversed(list):
        accumulator = function(item, accumulator)
    return accumulator

# Replicate exactly the test case 
print("foldr(lambda acc, el: el / acc, [1, 2, 3, 4], 24)")
result = foldr(lambda acc, el: el / acc, [1, 2, 3, 4], 24)
print(f"Result = {result}")
print(f"Expected = 9")

# Let's do it step by step exactly with print debugging
print("\n--- Step-by-step ---")
accumulator = 24
print(f"Initial accumulator = {accumulator}")

item = 4  # from right to left
print(f"Processing item {item}")
result1 = (lambda acc, el: el / acc)(item, accumulator) 
print(f"function({item}, {accumulator}) = {result1}")
accumulator = result1

item = 3
print(f"Processing item {item}")
result2 = (lambda acc, el: el / acc)(item, accumulator) 
print(f"function({item}, {accumulator}) = {result2}")
accumulator = result2

item = 2
print(f"Processing item {item}")
result3 = (lambda acc, el: el / acc)(item, accumulator) 
print(f"function({item}, {accumulator}) = {result3}")
accumulator = result3

item = 1
print(f"Processing item {item}")
result4 = (lambda acc, el: el / acc)(item, accumulator) 
print(f"function({item}, {accumulator}) = {result4}")

print(f"Final result (should be 9): {result4}")