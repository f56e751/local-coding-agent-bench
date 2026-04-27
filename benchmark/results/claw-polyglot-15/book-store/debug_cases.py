import sys
sys.path.insert(0, '/PublicSSD/minu/local-claude-project/benchmark/results/claw-polyglot-15/book-store')

from book_store import total

# Test the two failing cases one by one
print("=== CASE 1: test_one_group_of_one_and_two_plus_three_groups_of_four_is_cheaper_than_one_group_of_each_size ===")
basket = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]
result = total(basket)
print(f"Basket: {basket}")
print(f"Result: {result} cents")
print(f"Expected: 10000 cents")

print("\n=== CASE 2: test_two_groups_of_four_is_cheaper_than_groups_of_five_and_three ===")
basket = [1, 1, 2, 3, 4, 4, 5, 5]
result = total(basket)
print(f"Basket: {basket}")
print(f"Result: {result} cents")  
print(f"Expected: 5120 cents")

print("\n=== DEBUGGING ===")
# Let's also test a simpler case 
print("Let's see how our algorithm handles some cases:")
simple = [1, 1, 2, 3, 4, 4, 5, 5]
result = total(simple)
print(f"Simple case [1,1,2,3,4,4,5,5]: {result} cents")