#!/usr/bin/env python3

import go_counting

def test_specific_case():
    # Replicate exactly what the failing test does
    board = go_counting.Board(["  B  ", " B B ", "B W B", " W W ", "  W  "])
    stone, territory = board.territory(x=0, y=1)
    
    print(f"Result: stone={stone}, territory={territory}")
    print(f"Expected: stone='B', territory={(0, 0), (0, 1), (1, 0)}")
    print()
    print("Analysis of coordinates:")
    for i, row in enumerate(["  B  ", " B B ", "B W B", " W W ", "  W  "]):
        print(f"Row {i}: {row}")
    
    print("Position (0,1) is 'B' = black stone")
    print("Position (0,0) is ' ' = empty")
    print("Position (1,0) is ' ' = empty")
    print("Position (0,1) connects to (0,0) and (1,0) through empty spaces")
    print("But position (0,1) itself is not empty, so territory shouldn't include it")
    
    print(f"Territory should be empty? {territory}")
    
    # Try calling territory for (0,0) instead
    print("\nTrying territory(0,0):")
    stone2, territory2 = board.territory(x=0, y=0)  
    print(f"Result: stone={stone2}, territory={territory2}")

if __name__ == '__main__':
    test_specific_case()