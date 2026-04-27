class BowlingGame:
    def __init__(self):
        self.rolls = []
        
    def roll(self, pins):
        if pins < 0:
            raise ValueError("Pin count cannot be negative")
        if pins > 10:
            raise ValueError("Pin count cannot exceed 10")
            
        # Game is complete if we already have 21 rolls (as max 10 frames with 2 rolls each plus 1 for a 3-roller)
        if len(self.rolls) >= 21:
            raise IndexError("Cannot roll if game already has ten frames")
            
        self.rolls.append(pins)
            
    def score(self):
        if not self.rolls:
            raise IndexError("Cannot score an empty game")
            
        # Process frames properly
        total = 0
        roll_index = 0
        
        for frame in range(10):
            if roll_index >= len(self.rolls):
                raise IndexError("Cannot score an incomplete game")
                
            if frame == 9:  # Tenth frame - special case
                if self.rolls[roll_index] == 10:  # Strike in 10th frame
                    # Need 2 more rolls for bonus
                    if roll_index + 1 >= len(self.rolls) or roll_index + 2 >= len(self.rolls):
                        raise IndexError("Bonus rolls for a strike in the last frame must be rolled before score can be calculated")
                    total += 10 + self.rolls[roll_index + 1] + self.rolls[roll_index + 2]
                    roll_index += 3
                elif self.rolls[roll_index] + self.rolls[roll_index + 1] == 10:  # Spare in 10th frame
                    # Need 1 more roll for bonus
                    if roll_index + 2 >= len(self.rolls):
                        raise IndexError("Bonus roll for a spare in the last frame must be rolled before score can be calculated")
                    total += 10 + self.rolls[roll_index + 2]
                    roll_index += 3
                else:  # Open frame in 10th frame
                    total += self.rolls[roll_index] + self.rolls[roll_index + 1]
                    roll_index += 2
            else:  # First 9 frames
                if self.rolls[roll_index] == 10:  # Strike
                    total += 10
                    # Bonus from next two rolls
                    if roll_index + 1 >= len(self.rolls):
                        raise IndexError("Cannot score an incomplete game")
                    total += self.rolls[roll_index + 1]
                    if roll_index + 2 >= len(self.rolls):
                        raise IndexError("Cannot score an incomplete game")
                    total += self.rolls[roll_index + 2]
                    roll_index += 1  # Strike uses 1 roll
                else:  # Not a strike (open or spare)
                    frame_sum = self.rolls[roll_index] + self.rolls[roll_index + 1]
                    if frame_sum > 10:
                        raise ValueError("Two rolls in a frame cannot score more than 10 points")
                    total += frame_sum
                    roll_index += 2
        
        return total