class StackUnderflowError(Exception):
    """Exception raised when Stack is not full.
       message: explanation of the error.
    """
    def __init__(self, message):
        self.message = message


def evaluate(input_list):
    # Initialize stack and word definitions
    stack = []
    definitions = {}
    
    # Process each line of input
    for input_string in input_list:
        # Parse input into tokens
        tokens = input_string.upper().split()
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Handle numbers
            if token.isdigit() or (token.startswith('-') and token[1:].isdigit()):
                stack.append(int(token))
            
            # Handle operations
            elif token == '+':
                if len(stack) < 2:
                    raise StackUnderflowError("Insufficient number of items in stack")
                b = stack.pop()
                a = stack.pop()
                stack.append(a + b)
                
            elif token == '-':
                if len(stack) < 2:
                    raise StackUnderflowError("Insufficient number of items in stack")
                b = stack.pop()
                a = stack.pop()
                stack.append(a - b)
                
            elif token == '*':
                if len(stack) < 2:
                    raise StackUnderflowError("Insufficient number of items in stack")
                b = stack.pop()
                a = stack.pop()
                stack.append(a * b)
                
            elif token == '/':
                if len(stack) < 2:
                    raise StackUnderflowError("Insufficient number of items in stack")
                b = stack.pop()
                a = stack.pop()
                if b == 0:
                    raise ZeroDivisionError("divide by zero")
                stack.append(a // b)  # Integer division
                
            # Handle stack manipulation operations
            elif token == 'DUP':
                if len(stack) < 1:
                    raise StackUnderflowError("Insufficient number of items in stack")
                stack.append(stack[-1])
                
            elif token == 'DROP':
                if len(stack) < 1:
                    raise StackUnderflowError("Insufficient number of items in stack")
                stack.pop()
                
            elif token == 'SWAP':
                if len(stack) < 2:
                    raise StackUnderflowError("Insufficient number of items in stack")
                a = stack.pop()
                b = stack.pop()
                stack.append(a)
                stack.append(b)
                
            elif token == 'OVER':
                if len(stack) < 2:
                    raise StackUnderflowError("Insufficient number of items in stack")
                a = stack[-2]
                stack.append(a)
                
            # Handle word definition
            elif token == ':':
                if i + 1 >= len(tokens):
                    raise ValueError("undefined operation")
                
                word_name = tokens[i+1]
                if word_name.isdigit() or (word_name.startswith('-') and word_name[1:].isdigit()):
                    raise ValueError("illegal operation")
                    
                # Find the end of the definition (marked by ;)
                j = i + 2
                definition_tokens = []
                while j < len(tokens):
                    if tokens[j] == ';':
                        break
                    definition_tokens.append(tokens[j])
                    j += 1
                    
                if j >= len(tokens) or tokens[j] != ';':
                    raise ValueError("undefined operation")
                    
                definitions[word_name] = definition_tokens
                i = j  # Skip past the ';'
                
            # Handle defined words
            elif token in definitions:
                # Instead of recursive token manipulation, let's evaluate the definition directly
                # by processing the tokens of the definition in reverse order
                def_tokens = definitions[token]
                # Process definition tokens in reverse because we want the last item executed first
                for def_token in reversed(def_tokens):
                    if def_token.isdigit() or (def_token.startswith('-') and def_token[1:].isdigit()):
                        # It's a number - add to stack
                        stack.append(int(def_token))
                    else:
                        # It's an operation or another word - add back to current processing
                        tokens.insert(i + 1, def_token)
                # Skip incrementing i to process this same token again
                continue
                
            else:
                raise ValueError("undefined operation")
                
            i += 1
    
    return stack