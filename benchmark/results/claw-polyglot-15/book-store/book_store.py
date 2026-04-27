def total(basket):
    from collections import Counter
    
    # Define discount rates
    def cost_of_group(group_size):
        discounts = {1: 1.00, 2: 0.95, 3: 0.90, 4: 0.80, 5: 0.75}
        return 8 * group_size * discounts[group_size]
    
    # Count books
    counter = Counter(basket)
    counts = [0] * 5
    for book, count in counter.items():
        if 1 <= book <= 5:
            counts[book - 1] = count

    # Memoization for DP
    memo = {}
    
    def min_price(counts):
        # Convert counts to tuple for hashing
        counts = tuple(counts)
        if counts in memo:
            return memo[counts]
        
        # Base case: no books left
        if sum(counts) == 0:
            return 0
        
        min_cost = float('inf')
        
        # Try all valid group sizes from 5 down to 1
        for group_size in range(5, 0, -1):
            # Check if we have enough books of different types to make a group of this size
            available_types = sum(1 for count in counts if count > 0)
            if available_types >= group_size:
                # Try forming a group of size group_size using available book types
                new_counts = list(counts)
                # We'll just greedily take the first group_size available books
                books_taken = 0
                for i in range(5):
                    if new_counts[i] > 0 and books_taken < group_size:
                        new_counts[i] -= 1
                        books_taken += 1
                
                # If we were able to take exactly group_size books (all different types)
                if books_taken == group_size:
                    cost = cost_of_group(group_size) + min_price(new_counts)
                    min_cost = min(min_cost, cost)
        
        memo[counts] = min_cost
        return min_cost
    
    # Handle empty basket
    if not basket:
        return 0
    
    # Calculate minimum price
    result = min_price(counts)
    # Return in cents to avoid floating point errors 
    # (Use round instead of int to be more accurate)
    return int(round(result * 100))