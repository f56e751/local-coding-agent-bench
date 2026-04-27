
# Simple unit test script to see if I can execute tests properly
import unittest
import sys
sys.path.insert(0, '.')

# Try a simple version of the exact test condition

try:
    from bowling import BowlingGame
    
    game = BowlingGame()
    
    # Case from actual test (should raise an exception but doesn't according to failing test)  
    rolls = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10]
    print('Rolling:', rolls)
    print('Total rolls:', len(rolls))
    for roll in rolls:
        game.roll(roll)
    
    try:
        score = game.score()
        print('ERROR: score() should have raised an exception but returned:', score)
    except Exception as e:
        print('Correctly raised exception:', type(e).__name__, ':', str(e))
        
except Exception as e:
    print('Error creating the game or rolling:', e)

