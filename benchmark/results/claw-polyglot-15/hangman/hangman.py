# Game status categories
# Change the values as you see fit
STATUS_WIN = 'win'
STATUS_LOSE = 'lose'
STATUS_ONGOING = 'ongoing'


class Hangman:
    def __init__(self, word):
        self.word = word
        self.remaining_guesses = 9
        self.status = STATUS_ONGOING
        self.guessed_letters = set()
        self.masked_word = ['_'] * len(word)

    def guess(self, char):
        # Check if game is already over
        if self.status != STATUS_ONGOING:
            raise ValueError("The game has already ended.")
        
        char = char.lower()
        
        # If letter was already guessed, it counts as a failure
        if char in self.guessed_letters:
            self.remaining_guesses -= 1
        else:
            self.guessed_letters.add(char)
            # Check if the guess is correct
            if char in self.word:
                # Update the masked word with correct letters
                for i, letter in enumerate(self.word):
                    if letter == char:
                        self.masked_word[i] = letter
            else:
                # Incorrect guess, decrease remaining guesses
                self.remaining_guesses -= 1
        
        # Check for win condition first
        if '_' not in self.masked_word:
            self.status = STATUS_WIN
        # Check for lose condition
        elif self.remaining_guesses < 0:
            # This handles the exact case where we went over the allowed attempts
            # If remaining guesses < 0, it means we had 0 or less guesses
            self.status = STATUS_LOSE

    def get_masked_word(self):
        return ''.join(self.masked_word)

    def get_status(self):
        return self.status
