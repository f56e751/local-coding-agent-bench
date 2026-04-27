# Task: food-chain

Implement the solution in `food_chain.py` so that every test in `food_chain_test.py` passes.

## Problem description

# Instructions

Generate the lyrics of the song 'I Know an Old Lady Who Swallowed a Fly'.

While you could copy/paste the lyrics, or read them from a file, this problem is much more interesting if you approach it algorithmically.

This is a [cumulative song][cumulative-song] of unknown origin.

This is one of many common variants.

```text
I know an old lady who swallowed a fly.
I don't know why she swallowed the fly. Perhaps she'll die.

I know an old lady who swallowed a spider.
It wriggled and jiggled and tickled inside her.
She swallowed the spider to catch the fly.
I don't know why she swallowed the fly. Perhaps she'll die.

I know an old lady who swallowed a bird.
How absurd to swallow a bird!
She swallowed the bird to catch the spider that wriggled and jiggled and tickled inside her.
She swallowed the spider to catch the fly.
I don't know why she swallowed the fly. Perhaps she'll die.

I know an old lady who swallowed a cat.
Imagine that, to swallow a cat!
She swallowed the cat to catch the bird.
She swallowed the bird to catch the spider that wriggled and jiggled and tickled inside her.
She swallowed the spider to catch the fly.
I don't know why she swallowed the fly. Perhaps she'll die.

I know an old lady who swallowed a dog.
What a hog, to swallow a dog!
She swallowed the dog to catch the cat.
She swallowed the cat to catch the bird.
She swallowed the bird to catch the spider that wriggled and jiggled and tickled inside her.
She swallowed the spider to catch the fly.
I don't know why she swallowed the fly. Perhaps she'll die.

I know an old lady who swallowed a goat.
Just opened her throat and swallowed a goat!
She swallowed the goat to catch the dog.
She swallowed the dog to catch the cat.
She swallowed the cat to catch the bird.
She swallowed the bird to catch the spider that wriggled and jiggled and tickled inside her.
She swallowed the spider to catch the fly.
I don't know why she swallowed the fly. Perhaps she'll die.

I know an old lady who swallowed a cow.
I don't know how she swallowed a cow!
She swallowed the cow to catch the goat.
She swallowed the goat to catch the dog.
She swallowed the dog to catch the cat.
She swallowed the cat to catch the bird.
She swallowed the bird to catch the spider that wriggled and jiggled and tickled inside her.
She swallowed the spider to catch the fly.
I don't know why she swallowed the fly. Perhaps she'll die.

I know an old lady who swallowed a horse.
She's dead, of course!
```

[cumulative-song]: https://en.wikipedia.org/wiki/Cumulative_song


## Files

- Starter: `food_chain.py`  (edit this)
- Tests:   `food_chain_test.py`  (do NOT edit; used for grading)

## Rules

- Only modify `food_chain.py`.  Do not edit the tests or create new files.
- Python stdlib only — no package installs.
- When you believe you are done, run `pytest food_chain_test.py -x -q` and confirm green.

## Previous attempt failed — test feedback

```
F
=================================== FAILURES ===================================
___________________________ FoodChainTest.test_bird ____________________________
food_chain_test.py:34: in test_bird
    self.assertEqual(
E   AssertionError: Lists differ: ['I k[117 chars]that It wriggled and jiggled and tickled insid[112 chars]ie."] != ['I k[117 chars]that wriggled and jiggled and tickled inside h[109 chars]ie."]
E   
E   First differing element 2:
E   'She [29 chars]he spider that It wriggled and jiggled and tickled inside her.'
E   'She [29 chars]he spider that wriggled and jiggled and tickled inside her.'
E   
E     ['I know an old lady who swallowed a bird.',
E      'How absurd to swallow a bird!',
E   -  'She swallowed the bird to catch the spider that It wriggled and jiggled and '
E   ?                                                  ---
E   
E   +  'She swallowed the bird to catch the spider that wriggled and jiggled and '
E      'tickled inside her.',
E      'She swallowed the spider to catch the fly.',
E      "I don't know why she swallowed the fly. Perhaps she'll die."]
=========================== short test summary info ============================
FAILED food_chain_test.py::FoodChainTest::test_bird - AssertionError: Lists d...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed in 0.01s


```

Fix the failures and try again.
