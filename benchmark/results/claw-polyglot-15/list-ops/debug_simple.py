#!/usr/bin/env python3

# Let me test a simpler example

def foldr_simple_test():
    print("Simpler test...")
    
    # This is what function actually does
    # For foldr(lambda acc, el: el / acc, [1, 2, 3, 4], 24)
    
    def my_foldr(function, lst, initial):
        accumulator = initial
        print(f"Starting with accumulator = {accumulator}")
        for item in reversed(lst):
            print(f"Calling function({item}, {accumulator})")
            old_acc = accumulator
            accumulator = function(item, accumulator)
            print(f"Result = {accumulator}")
        return accumulator

    result = my_foldr(lambda acc, el: el / acc, [1, 2, 3, 4], 24)
    print(f"Final result = {result}")
    
    print()
    print("Let's think step-by-step:")
    print("In lambda acc, el: el / acc, when called as function(4, 24):")
    print("acc = 4, el = 24")
    print("return value = el / acc = 24 / 4 = 6")
    print("This means the function call is swapping parameters!")

foldr_simple_test()