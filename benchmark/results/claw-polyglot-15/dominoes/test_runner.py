#!/usr/bin/env python3

import dominoes

def test_empty_input_empty_output():
    input_dominoes = []
    output_chain = dominoes.can_chain(input_dominoes)
    print(f"Empty input test: {output_chain}")
    assert output_chain == []

def test_singleton_input_singleton_output():
    input_dominoes = [(1, 1)]
    output_chain = dominoes.can_chain(input_dominoes)
    print(f"Singleton input test: {output_chain}")
    assert output_chain == [(1, 1)]

def test_singleton_that_can_t_be_chained():
    input_dominoes = [(1, 2)]
    output_chain = dominoes.can_chain(input_dominoes)
    print(f"Singleton that can't be chained test: {output_chain}")
    assert output_chain is None

def test_three_elements():
    input_dominoes = [(1, 2), (3, 1), (2, 3)]
    output_chain = dominoes.can_chain(input_dominoes)
    print(f"Three elements test: {output_chain}")
    assert output_chain is not None
    # Validate the chain manually
    if output_chain:
        assert output_chain[0][0] == output_chain[-1][1]  # First and last match
        assert output_chain[0][1] == output_chain[1][0]  # First two match
        assert output_chain[1][1] == output_chain[2][0]  # Second and third match

def test_can_reverse_dominoes():
    input_dominoes = [(1, 2), (1, 3), (2, 3)]
    output_chain = dominoes.can_chain(input_dominoes)
    print(f"Can reverse dominoes test: {output_chain}")
    assert output_chain is not None

def test_can_t_be_chained():
    input_dominoes = [(1, 2), (4, 1), (2, 3)]
    output_chain = dominoes.can_chain(input_dominoes)
    print(f"Can't be chained test: {output_chain}")
    assert output_chain is None

def test_disconnected_simple():
    input_dominoes = [(1, 1), (2, 2)]
    output_chain = dominoes.can_chain(input_dominoes)
    print(f"Disconnected simple test: {output_chain}")
    assert output_chain is None

if __name__ == "__main__":
    try:
        test_empty_input_empty_output()
        print("✓ Empty input test passed")
        
        test_singleton_input_singleton_output()
        print("✓ Singleton input test passed")
        
        test_singleton_that_can_t_be_chained()
        print("✓ Singleton that can't be chained test passed")
        
        test_three_elements()
        print("✓ Three elements test passed")
        
        test_can_reverse_dominoes()
        print("✓ Can reverse dominoes test passed")
        
        test_can_t_be_chained()
        print("✓ Can't be chained test passed")
        
        test_disconnected_simple()
        print("✓ Disconnected simple test passed")
        
        print("\nAll tests passed! ✓")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()