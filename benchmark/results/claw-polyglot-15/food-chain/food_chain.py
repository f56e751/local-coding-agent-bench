def recite(start_verse, end_verse):
    # Define the animals and their special comments
    animals = [
        {"name": "fly", "comment": "I don't know why she swallowed the fly. Perhaps she'll die."},
        {"name": "spider", "comment": "It wriggled and jiggled and tickled inside her."},
        {"name": "bird", "comment": "How absurd to swallow a bird!"},
        {"name": "cat", "comment": "Imagine that, to swallow a cat!"},
        {"name": "dog", "comment": "What a hog, to swallow a dog!"},
        {"name": "goat", "comment": "Just opened her throat and swallowed a goat!"},
        {"name": "cow", "comment": "I don't know how she swallowed a cow!"},
        {"name": "horse", "comment": "She's dead, of course!"}
    ]
    
    result = []
    
    for i in range(start_verse - 1, end_verse):
        # First line: introduction
        result.append(f"I know an old lady who swallowed a {animals[i]['name']}.")
        
        # Special comment for this animal
        result.append(animals[i]["comment"])
        
        # If this is the horse verse, we're done
        if i == len(animals) - 1:
            continue
        
        # Catching sequence - from the current animal backwards towards fly
        # Build lines of "She swallowed the X to catch the Y" 
        # where the catch Y may include a "that comment" depending on context
        
        # This goes backwards from current animal index to 1
        for step in range(i, 0, -1):
            # step refers to which animal we're currently catching 
            # step-1 refers to what animal is being caught
            
            if step == 1:
                # Final catch to fly 
                result.append(f"She swallowed the {animals[step]['name']} to catch the {animals[step-1]['name']}.")
            else:
                # Intermediate catch - add "that" construction from the caught animal's comment
                caught_comment = animals[step-1]["comment"]
                if caught_comment.startswith("It "):
                    caught_comment = caught_comment[3:]  # Remove "It "
                result.append(f"She swallowed the {animals[step]['name']} to catch the {animals[step-1]['name']} that {caught_comment}")
        
        # Final line (should be just once)
        result.append(animals[0]["comment"])
        
        # Add empty line between verses (except after the last one)
        if i < end_verse - 1:
            result.append("")
    
    return result