import sys
sys.path.insert(0, '/PublicSSD/minu/local-claude-project/benchmark/results/claw-polyglot-15/book-store')

from book_store import total

# Test the specific failing case
basket = [1, 1, 2, 2, 3, 4]
result = total(basket)
print(f"Test case [1, 1, 2, 2, 3, 4]: got {result} cents")

# Test a few other cases to see if our logic works
test_cases = [
    ([1], 800),
    ([1, 2], 1520),
    ([1, 2, 3], 2160),
    ([1, 2, 3, 4], 2560),
    ([1, 2, 3, 4, 5], 3000),
    ([1, 1, 2, 2, 3, 4], 4080),  # This is the failing case
]

print("\nTesting various cases:")
for i, (basket, expected) in enumerate(test_cases):
    result = total(basket)
    status = "PASS" if result == expected else "FAIL"
    print(f"Test {i+1}: {basket} -> {result} cents (expected {expected}) [{status}]")