def encode(plain_text, a, b):
    m = 26  # size of alphabet
    
    # Check if a and m are coprime
    if gcd(a, m) != 1:
        raise ValueError("a and m must be coprime.")
    
    result = []
    for char in plain_text:
        if char.isalpha():
            # Convert to lowercase and get index (0-25)
            i = ord(char.lower()) - ord('a')
            # Apply encryption formula: E(x) = (ai + b) mod m
            encrypted_index = (a * i + b) % m
            # Convert back to character
            result.append(chr(encrypted_index + ord('a')))
        elif char.isdigit():
            # Digits are not encrypted
            result.append(char)
        # Skip spaces and punctuation
    
    # Group into chunks of 5
    grouped = []
    for i, char in enumerate(result):
        if i % 5 == 0 and i != 0:
            grouped.append(' ')
        grouped.append(char)
    
    return ''.join(grouped)


def decode(ciphered_text, a, b):
    m = 26  # size of alphabet
    
    # Check if a and m are coprime
    if gcd(a, m) != 1:
        raise ValueError("a and m must be coprime.")
    
    # Find modular multiplicative inverse of a
    a_inv = mod_inverse(a, m)
    
    result = []
    for char in ciphered_text:
        if char.isalpha():
            # Get index of the character (0-25)
            y = ord(char.lower()) - ord('a')
            # Apply decryption formula: D(y) = a^-1 * (y - b) mod m
            decrypted_index = (a_inv * (y - b)) % m
            # Convert back to character
            result.append(chr(decrypted_index + ord('a')))
        elif char.isdigit():
            # Digits are not decrypted
            result.append(char)
        # Skip spaces and punctuation
    
    return ''.join(result)


def gcd(a, b):
    """Calculate the Greatest Common Divisor of a and b."""
    while b:
        a, b = b, a % b
    return a


def mod_inverse(a, m):
    """Calculate the modular multiplicative inverse of a mod m."""
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None  # Should never happen if a and m are coprime