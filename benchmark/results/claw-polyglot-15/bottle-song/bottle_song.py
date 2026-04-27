def recite(start, take=1):
    # Number to word mapping
    number_words = {
        10: "Ten",
        9: "Nine", 
        8: "Eight",
        7: "Seven",
        6: "Six",
        5: "Five",
        4: "Four",
        3: "Three",
        2: "Two",
        1: "One"
    }
    
    # Function to get the plural form
    def plural(n):
        return "bottle" if n == 1 else "bottles"
    
    verses = []
    
    for i in range(take):
        current = start - i
        if current <= 0:
            break
            
        next_count = current - 1
        
        # Format the current number (always capitalized)
        current_word = number_words[current]
        
        # Format the next number
        if next_count == 0:
            next_word = "no"
            next_plural = "bottles"
        else:
            next_word = number_words[next_count].lower()  # Make lowercase for the "There'll be" line
            next_plural = plural(next_count)
        
        # Generate the verse
        verse = [
            f"{current_word} green {plural(current)} hanging on the wall,",
            f"{current_word} green {plural(current)} hanging on the wall,",
            "And if one green bottle should accidentally fall,",
            f"There'll be {next_word} green {next_plural} hanging on the wall."
        ]
        
        verses.extend(verse)
        
        # Add empty line between verses (except after the last one)
        if i < take - 1:
            verses.append("")
    
    return verses
