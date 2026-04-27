def grep(pattern, flags, files):
    # Parse flags
    flag_n = '-n' in flags
    flag_l = '-l' in flags
    flag_i = '-i' in flags
    flag_v = '-v' in flags
    flag_x = '-x' in flags
    
    # Prepare pattern for case-insensitive matching
    search_pattern = pattern if not flag_i else pattern.lower()
    
    # Track which files have matches for -l flag
    matching_files = set()
    
    # Results storage
    results = []
    
    # Process each file in order
    for filename in files:
        try:
            # Read file line by line
            with open(filename, 'r') as f:
                line_num = 0
                for line in f:
                    line_num += 1
                    # Remove newline for matching
                    line_content = line.rstrip('\n')
                    
                    # Check if line matches our pattern
                    match = False
                    if flag_x:
                        # Match entire line
                        if flag_i:
                            match = line_content.lower() == search_pattern
                        else:
                            match = line_content == search_pattern
                    else:
                        # Partial matching
                        if flag_i:
                            match = search_pattern in line_content.lower()
                        else:
                            match = search_pattern in line_content
                    
                    # Apply invert flag
                    if flag_v:
                        match = not match
                    
                    if match:
                        # If -l flag, just track the file
                        if flag_l:
                            matching_files.add(filename)
                        else:
                            # Build output line
                            output = ""
                            if len(files) > 1:
                                output += f"{filename}:"
                            if flag_n:
                                output += f"{line_num}:"
                            output += line_content
                            results.append(output)
        except FileNotFoundError:
            # If a file doesn't exist, skip it (as per normal grep behavior)
            pass
    
    # If -l flag is used, return only filenames
    if flag_l:
        return '\n'.join(sorted(matching_files)) + '\n' if matching_files else ''
    
    # Return results
    return '\n'.join(results) + '\n' if results else ''
