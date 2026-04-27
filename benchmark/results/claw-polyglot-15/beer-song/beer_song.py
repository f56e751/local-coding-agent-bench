def recite(start, take=1):
    result = []
    
    # Generate the verses in reverse order as specified by the parameters
    for i in range(start, start - take, -1):
        if i < 0:
            break
            
        if i == 0:
            result.append("No more bottles of beer on the wall, no more bottles of beer.")
            result.append("Go to the store and buy some more, 99 bottles of beer on the wall.")
        elif i == 1:
            result.append("1 bottle of beer on the wall, 1 bottle of beer.")
            result.append("Take it down and pass it around, no more bottles of beer on the wall.")
        elif i == 2:
            result.append("2 bottles of beer on the wall, 2 bottles of beer.")
            result.append("Take one down and pass it around, 1 bottle of beer on the wall.")
        else:
            result.append(f"{i} bottles of beer on the wall, {i} bottles of beer.")
            result.append(f"Take one down and pass it around, {i-1} bottles of beer on the wall.")
            
        # Add a blank line between verses, but not after the last verse
        # We add blank line if we're NOT at the last verse we're generating
        if i > start - take + 1:
            result.append("")
    
    return result